# F20j (HPP-629, ROADMAP s122 item 550(z)): the KYTY_DIAG_B32 / KYTY_TEST_B32 sites. Usage: python patch_f20j.py <root>
# Anchors are whole lines (compared stripped), searched inside an optional scope (first line .. end line, both whole
# lines); every anchor must match exactly once (or the named occurrence). Inserted text: '»' = one tab. CRLF files keep
# CRLF, LF files keep LF (write_bytes).
import os
import sys

ROOT = sys.argv[1]
TAB = chr(9)
fails = []
done = []


def load(rel):
    b = open(os.path.join(ROOT, rel), 'rb').read()
    crlf = b'\r\n' in b
    t = b.decode('utf-8').replace('\r\n', '\n')
    return t, crlf


def save(rel, t, crlf):
    if crlf:
        t = t.replace('\n', '\r\n')
    open(os.path.join(ROOT, rel), 'wb').write(t.encode('utf-8'))


def block(text):
    lines = text.strip('\n').split('\n')
    return [l.replace('»', TAB) for l in lines]


class F:
    def __init__(self, rel):
        self.rel = rel
        self.t, self.crlf = load(rel)
        self.lines = self.t.split('\n')

    def find(self, anchor, scope=None, nth=None):
        lo, hi = 0, len(self.lines)
        if scope is not None:
            s = [i for i, l in enumerate(self.lines) if l.strip() == scope[0].strip()]
            if len(s) != 1:
                fails.append('%s: scope start %r matches %d' % (self.rel, scope[0], len(s)))
                return None
            lo = s[0]
            e = [i for i in range(lo + 1, len(self.lines)) if self.lines[i].strip() == scope[1].strip()]
            if not e:
                fails.append('%s: scope end %r not found' % (self.rel, scope[1]))
                return None
            hi = e[0] + 1
        m = [i for i in range(lo, hi) if self.lines[i].strip() == anchor.strip()]
        if nth is not None:
            if len(m) <= nth:
                fails.append('%s: anchor %r occurrence %d of %d' % (self.rel, anchor, nth, len(m)))
                return None
            return m[nth]
        if len(m) != 1:
            fails.append('%s: anchor %r matches %d (scope %r)' % (self.rel, anchor, len(m), scope))
            return None
        return m[0]

    def ins(self, anchor, text, where='after', scope=None, nth=None, tag=''):
        i = self.find(anchor, scope, nth)
        if i is None:
            return
        new = block(text)
        at = i + 1 if where == 'after' else i
        self.lines[at:at] = new
        done.append('%s: %s %s %r (+%d)' % (self.rel, tag, where, anchor.strip()[:60], len(new)))

    def save(self):
        save(self.rel, '\n'.join(self.lines), self.crlf)


INC = '#include "common/diagB32.h"'

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/common/frameStats.h')
f.ins('[[nodiscard]] uint64_t ProcessCpuNs();', '''
// Track F, F20j (KYTY_DIAG_B32, RC4): the TSC calibration ThreadCpuNs converts QueryThreadCycleTime with (0 off Windows).
[[nodiscard]] double     CpuCyclesPerNs();
''', tag='decl')
f.save()

f = F('src/common/frameStats.cpp')
f.ins('#include "common/frameStats.h"', INC, tag='include')
f.ins('uint64_t ProcessCpuNs() {', '''
double CpuCyclesPerNs() {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
»return TscCyclesPerNs();
#else
»return 0.0;
#endif
}

''', where='before', tag='CpuCyclesPerNs')
f.ins('StartSampler(role);', '''
»// Track F, F20j (KYTY_DIAG_B32, RC2): the role's slot of the B32 sampler (Main, Gpu, Present, Record).
»if (Common::DiagB32::g_on) [[unlikely]] {
»»static constexpr const char* names[] = {"Main", "Gpu", "Present", "Record"};
»»Common::DiagB32::RegisterRole(static_cast<size_t>(role) < 4 ? names[static_cast<size_t>(role)] : "emu");
»}
''', where='before', scope=('void RegisterCurrentThread(ThreadRole role) {', 'ThreadRole CurrentRole() {'), tag='role')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/emulator.cpp')
f.ins('#include "common/assert.h"', INC, tag='include')
f.ins('void Run(const RunOptions& options) {', '''
»// Track F, F20j: KYTY_DIAG_B32 / KYTY_TEST_B32 are read here once, before any guest thread (RC10).
»Common::DiagB32::Init();
''', tag='init')
f.ins('PrintSystemInfo();', '''
»Common::DiagB32::LogHeader(); // Track F, F20j: "DiagB32: mode=1 ..." / "TestB32: config ..." once
''', scope=('void Run(const RunOptions& options) {', 'Execute(options.game_patch);'), tag='header')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/kernel/pthread.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
f.ins('std::atomic<uint64_t> pending_signal_mask {0};', '''
»// Track F, F20j (KYTY_DIAG_B32): host-heap fields, never seen by the guest (the guest sees `guest` only); written
»// only at KYTY_DIAG_B32=1 (value-initialized with the object like every other field).
»std::atomic<int32_t>  b32_slot1 {0}; // DiagB32 slot + 1 of this thread
»std::atomic<uint64_t> b32_waker {0}; // DiagB32::PackSig of the thread whose Signal/Broadcast advanced cond_sequence
''', scope=('struct PthreadPrivate {', '};'), tag='fields')
f.ins('thread->cond_sequence++;', '''
»if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (M2 cond): the waker of this waiter
»»thread->b32_waker.store(Common::DiagB32::PackSig(), std::memory_order_relaxed);
»}
''', scope=('static void CondWakeWaiter(PthreadCondPrivate* cond, Pthread thread) {', 'void PthreadWakeForSignal(Pthread thread) {'), tag='wake')
f.ins('thread->cond_sequence++;', '''
»»if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (M2 cond): the waker of every waiter
»»»thread->b32_waker.store(Common::DiagB32::PackSig(), std::memory_order_relaxed);
»»}
''', scope=('int KYTY_SYSV_ABI PthreadCondBroadcast(PthreadCond* cond) {', 'int KYTY_SYSV_ABI PthreadCondDestroy(PthreadCond* cond) {'), tag='broadcast')
f.ins('g_pthread_self->unique_id       = Common::Thread::GetThreadIdUnique();', '''
»if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j: the guest main thread's slot (registered as role Main)
»»g_pthread_self->b32_slot1.store(Common::DiagB32::RegisterGuest(g_pthread_self->unique_id, "MainThread"),
»»                                 std::memory_order_relaxed);
»}
''', scope=('void PthreadInitSelfForMainThread() {', 'uint64_t os_thread_id = 0;'), tag='main')
# NativeMutexLock: W:mutex on the slow path (RC5(a)).
SC = ('static int NativeMutexLock(PthreadMutexPrivate* mutex, KernelUseconds* timeout_us) {',
      'static int NativeMutexTrylock(PthreadMutexPrivate* mutex) {')
f.ins('if (timeout_us == nullptr) {', '''
»// Track F, F20j (KYTY_DIAG_B32, RC5(a)): W:mutex only on the slow path (another thread owns the mutex) - this also
»// covers NativeMutexLockRecurse, the re-lock after a cond wait. The peer is the owner at entry.
»Common::DiagB32::Mark b32;
»if (Common::DiagB32::g_on && mutex->owner != nullptr && (timeout_us == nullptr || *timeout_us > 0)) [[unlikely]] {
»»b32.BeginW(Common::DiagB32::Wait::Mutex, mutex, mutex->owner->b32_slot1.load(std::memory_order_relaxed),
»»           timeout_us != nullptr ? static_cast<uint64_t>(*timeout_us) : 0);
»}
''', where='before', scope=SC, tag='mutex-begin')
f.ins('return ETIMEDOUT;', '''
»»»»b32.EndWithPeer(true);
''', where='before', scope=SC, nth=2, tag='mutex-to')
f.ins('mutex->owner = self;', '''
»b32.EndWithPeer(false);
''', where='before', scope=SC, tag='mutex-end')
# Cond waits (M2): W:cond over the wait loop.
for name, req in (('PthreadCondTimedwait', 'static_cast<uint64_t>(usec)'),
                  ('PthreadCondTimedwaitAbs', 'B32ReqUs(deadline)'),
                  ('PthreadCondWait', '0')):
    if name == 'PthreadCondTimedwait':
        sc = ('int KYTY_SYSV_ABI PthreadCondTimedwait(PthreadCond* cond, PthreadMutex* mutex,',
              'int KYTY_SYSV_ABI PthreadCondTimedwaitAbs(PthreadCond* cond, PthreadMutex* mutex,')
    elif name == 'PthreadCondTimedwaitAbs':
        sc = ('int KYTY_SYSV_ABI PthreadCondTimedwaitAbs(PthreadCond* cond, PthreadMutex* mutex,',
              'int KYTY_SYSV_ABI PthreadCondWait(PthreadCond* cond, PthreadMutex* mutex) {')
    else:
        sc = ('int KYTY_SYSV_ABI PthreadCondWait(PthreadCond* cond, PthreadMutex* mutex) {', 'Pthread KYTY_SYSV_ABI PthreadSelf() {')
    f.ins('auto ready = [thread, thread_sequence] { return thread->cond_sequence != thread_sequence; };', '''
»// Track F, F20j (KYTY_DIAG_B32, M2 cond): W:cond over the wait loop; the waker - the thread whose Signal / Broadcast
»// advanced cond_sequence (b32_waker); a timeout has none.
»Common::DiagB32::Mark b32;
»if (Common::DiagB32::g_on) [[unlikely]] {
»»b32.BeginW(Common::DiagB32::Wait::Cond, cond_value, 0, %s);
»}
''' % req, scope=sc, tag='cond-begin ' + name)
    f.ins('CondRemoveWaiter(cond_value, thread);', '''
»if (b32.Active()) [[unlikely]] {
»»b32.End(ready() ? Common::DiagB32::SigWaker(thread->b32_waker.load(std::memory_order_relaxed), b32.SinceNs()) : 0,
»»        !ready());
»}
''', where='before', scope=sc, nth=1, tag='cond-end ' + name)
f.ins('static bool NativeCondDeadlineFromAbs(KernelClockid clock_id, const KernelTimespec* abstime,', '''
// Track F, F20j (KYTY_DIAG_B32): the requested time of an absolute cond wait, us (0 if already past).
static uint64_t B32ReqUs(std::chrono::steady_clock::time_point deadline) {
»const auto now = std::chrono::steady_clock::now();
»return deadline > now ? static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::microseconds>(deadline - now).count())
»                      : 0;
}

''', where='before', tag='B32ReqUs')
f.ins('static_cast<uint64_t>(thread->attr->stack_size));', '''
»if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (KYTY_DIAG_B32): the guest thread's slot, name and id
»»thread->b32_slot1.store(Common::DiagB32::RegisterGuest(thread->unique_id, thread->name.c_str()),
»»                        std::memory_order_relaxed);
»}
''', scope=('static void* RunThread(void* arg) {', 'int KYTY_SYSV_ABI PthreadCreate(Pthread* thread, const PthreadAttr* attr,'), nth=0, tag='run')
f.ins('thread->almost_done = true;', '''
»if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j: the slot stops being sampled
»»Common::DiagB32::Unregister();
»}
''', where='before', scope=('static void CleanupThread(void* arg) {', '// KYTY_PRINT_NAMES_THREADS=<name>[,<name>...]: PRINT_NAME on the listed guest threads only.'), tag='cleanup')
SLEEP = '''
»Common::DiagB32::Mark b32; // Track F, F20j (KYTY_DIAG_B32, RC5(b)): W:sleep with the requested time, no waker
»if (Common::DiagB32::g_on) [[unlikely]] {
»»b32.BeginW(Common::DiagB32::Wait::Sleep, nullptr, 0, %s);
»}
'''
f.ins('SleepMicroWithSignalPoll(microseconds);', SLEEP % 'static_cast<uint64_t>(microseconds)', where='before',
      scope=('int KYTY_SYSV_ABI KernelUsleep(KernelUseconds microseconds) {', 'unsigned int KYTY_SYSV_ABI KernelSleep(unsigned int seconds) {'), tag='usleep')
f.ins('SleepMicroWithSignalPoll(microseconds);', '»b32.End(0, true);',
      scope=('int KYTY_SYSV_ABI KernelUsleep(KernelUseconds microseconds) {', 'unsigned int KYTY_SYSV_ABI KernelSleep(unsigned int seconds) {'), tag='usleep-end')
f.ins('SleepMicroWithSignalPoll(static_cast<uint64_t>(seconds) * 1000000ull);', SLEEP % 'static_cast<uint64_t>(seconds) * 1000000ull',
      where='before', tag='sleep')
f.ins('SleepMicroWithSignalPoll(static_cast<uint64_t>(seconds) * 1000000ull);', '»b32.End(0, true);', tag='sleep-end')
f.ins('SleepNanoWithSignalPoll(nanos);', SLEEP % 'nanos / 1000u', where='before',
      scope=('int KYTY_SYSV_ABI KernelNanosleep(const KernelTimespec* rqtp, KernelTimespec* rmtp) {', 'if (rmtp != nullptr) {'), tag='nanosleep')
f.ins('SleepNanoWithSignalPoll(nanos);', '»b32.End(0, true);',
      scope=('int KYTY_SYSV_ABI KernelNanosleep(const KernelTimespec* rqtp, KernelTimespec* rmtp) {', 'if (rmtp != nullptr) {'), tag='nanosleep-end')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/kernel/semaphore.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
f.ins('int                         m_max_count;', '''
»// Track F, F20j (KYTY_DIAG_B32, M2 sem): DiagB32::PackSig of the last Signal / Cancel; written only at =1.
»std::atomic<uint64_t> m_b32_sig {0};
''', scope=('class KernelSemaPrivate {', 'KernelSemaPrivate::~KernelSemaPrivate() {'), tag='field')
f.ins('WakeWaiters();', '''
»if (Common::DiagB32::g_on) [[unlikely]] {
»»m_b32_sig.store(Common::DiagB32::PackSig(), std::memory_order_relaxed); // Track F, F20j (M2 sem)
»}
''', where='before', scope=('KernelSemaPrivate::Result KernelSemaPrivate::Signal(int signal_count) {', 'void KernelSemaPrivate::AddWaiter(WaitingThread* waiter) {'), tag='signal')
f.ins('AddWaiter(&waiter);', '''
»// Track F, F20j (KYTY_DIAG_B32, M2 sem): W:sem on the blocking path; the waker - the last Signal.
»Common::DiagB32::Mark b32;
»if (Common::DiagB32::g_on) [[unlikely]] {
»»b32.BeginW(Common::DiagB32::Wait::Sem, this, 0, infinitely ? 0 : static_cast<uint64_t>(micros));
»}
''', scope=('KernelSemaPrivate::Result KernelSemaPrivate::Wait(int need_count, uint32_t* ptr_micros) {', 'int KYTY_SYSV_ABI KernelCreateSema(KernelSema* sem, const char* name, uint32_t attr, int init,'), tag='wait-begin')
f.ins('*ptr_micros = 0;', '''
»»»b32.End(0, true);
''', scope=('KernelSemaPrivate::Result KernelSemaPrivate::Wait(int need_count, uint32_t* ptr_micros) {', 'int KYTY_SYSV_ABI KernelCreateSema(KernelSema* sem, const char* name, uint32_t attr, int init,'), tag='wait-to')
f.ins('RemoveWaiter(&waiter);', '''
»if (b32.Active()) [[unlikely]] {
»»b32.End(waiter.result == Result::Ok ? Common::DiagB32::SigWaker(m_b32_sig.load(std::memory_order_relaxed), b32.SinceNs()) : 0,
»»        false);
»}
''', where='before', scope=('KernelSemaPrivate::Result KernelSemaPrivate::Wait(int need_count, uint32_t* ptr_micros) {', 'int KYTY_SYSV_ABI KernelCreateSema(KernelSema* sem, const char* name, uint32_t attr, int init,'), nth=1, tag='wait-end')
# POSIX semaphore (the second semaphore of libkernel; same member M2 sem, kind psem).
PS = ('int Wait(uint32_t* micros) {', 'int TryWait() {')
f.ins('while (m_count <= 0) {', '''
»»// Track F, F20j (KYTY_DIAG_B32, M2 sem): W:psem on the blocking path; the waker - the last Post.
»»Common::DiagB32::Mark b32;
»»if (Common::DiagB32::g_on && m_count <= 0) [[unlikely]] {
»»»b32.BeginW(Common::DiagB32::Wait::PSem, this, 0, timed_wait ? static_cast<uint64_t>(*micros) : 0);
»»}
''', where='before', scope=PS, tag='psem-begin')
f.ins('SyncGuest();', '''
»»»»b32.End(0, true);
''', where='before', scope=PS, nth=0, tag='psem-to')
f.ins('m_count--;', '''
»»if (b32.Active()) [[unlikely]] {
»»»b32.End(Common::DiagB32::SigWaker(m_b32_sig.load(std::memory_order_relaxed), b32.SinceNs()), false);
»»}
''', where='before', scope=PS, tag='psem-end')
f.ins('m_count++;', '''
»»if (Common::DiagB32::g_on) [[unlikely]] {
»»»m_b32_sig.store(Common::DiagB32::PackSig(), std::memory_order_relaxed); // Track F, F20j (M2 sem)
»»}
''', where='before', scope=('int Post() {', 'int GetValue() {'), tag='psem-post')
f.ins('uint32_t        m_waiters = 0;', '''
»// Track F, F20j (KYTY_DIAG_B32): DiagB32::PackSig of the last Post (host object); written only at =1.
»std::atomic<uint64_t> m_b32_sig {0};
''', tag='psem-field')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/kernel/eventFlag.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
f.ins('uint64_t        m_bits          = 0;', '''
»// Track F, F20j (KYTY_DIAG_B32, M2 event flag): DiagB32::PackSig of the last Set; written only at =1.
»std::atomic<uint64_t> m_b32_sig {0};
''', scope=('class KernelEventFlagPrivate {', 'namespace {'), tag='field')
EW = ('KernelEventFlagPrivate::Result KernelEventFlagPrivate::Wait(uint64_t bits, WaitMode wait_mode,', 'void KernelEventFlagPrivate::Set(uint64_t bits) {')
f.ins('m_waiting_threads++;', '''
»»// Track F, F20j (KYTY_DIAG_B32, M2 event flag): W:evf from the first blocking pass; the waker - the last Set.
»»if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {
»»»b32.BeginW(Common::DiagB32::Wait::Evf, this, 0, infinitely ? 0 : static_cast<uint64_t>(micros));
»»}
''', where='before', scope=EW, tag='evf-begin')
f.ins('if (m_single_thread && m_waiting_threads > 0) {', '''
»Common::DiagB32::Mark b32; // Track F, F20j (KYTY_DIAG_B32): begun below only on the blocking path
''', where='before', scope=EW, tag='evf-decl')
f.ins('update_timeout();', '''
»»»b32.End(0, true);
''', where='before', scope=EW, nth=0, tag='evf-to')
f.ins('if (result != nullptr) {', '''
»if (b32.Active()) [[unlikely]] {
»»b32.End(Common::DiagB32::SigWaker(m_b32_sig.load(std::memory_order_relaxed), b32.SinceNs()), false);
»}
''', where='before', scope=EW, nth=3, tag='evf-end')
f.ins('m_bits |= bits;', '''
»if (Common::DiagB32::g_on) [[unlikely]] {
»»m_b32_sig.store(Common::DiagB32::PackSig(), std::memory_order_relaxed); // Track F, F20j (M2 event flag)
»}
''', scope=('void KernelEventFlagPrivate::Set(uint64_t bits) {', 'void KernelEventFlagPrivate::Clear(uint64_t bits) {'), tag='set')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/kernel/eventQueue.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
f.ins('bool                         m_closed = false;', '''
»// Track F, F20j (KYTY_DIAG_B32, M2 event queue): DiagB32::PackSig of the last TriggerEvent / AddEvent; =1 only.
»std::atomic<uint64_t> m_b32_sig {0};
''', scope=('class KernelEqueuePrivate {', 'KernelEqueuePrivate::~KernelEqueuePrivate() {'), tag='field')
WE = ('int KernelEqueuePrivate::WaitForEvents(KernelEvent* ev, int num, uint32_t micros) {', 'int KernelEqueuePrivate::AddEvent(const KernelEqueueEvent& event) {')
f.ins('for (;;) {', '''
»// Track F, F20j (KYTY_DIAG_B32, M2 event queue): W:eq over the wait; the waker - the last trigger in the wait.
»Common::DiagB32::Mark b32;
»if (Common::DiagB32::g_on) [[unlikely]] {
»»b32.BeginW(Common::DiagB32::Wait::Eq, this, 0, micros);
»}
''', where='before', scope=WE, tag='eq-begin')
f.ins('return ret;', '''
»»»if (b32.Active()) [[unlikely]] {
»»»»b32.End(ret > 0 ? Common::DiagB32::SigWaker(m_b32_sig.load(std::memory_order_relaxed), b32.SinceNs()) : 0, ret == 0);
»»»}
''', where='before', scope=WE, nth=0, tag='eq-end')
f.ins('m_cond_var.Signal();', '''
»if (Common::DiagB32::g_on) [[unlikely]] {
»»m_b32_sig.store(Common::DiagB32::PackSig(), std::memory_order_relaxed); // Track F, F20j (M2 event queue)
»}
''', where='before', scope=('int KernelEqueuePrivate::AddEvent(const KernelEqueueEvent& event) {', 'int KernelEqueuePrivate::TriggerEvent(uintptr_t ident, int16_t filter, void* trigger_data) {'), tag='add')
f.ins('m_cond_var.Signal();', '''
»»if (Common::DiagB32::g_on) [[unlikely]] {
»»»m_b32_sig.store(Common::DiagB32::PackSig(), std::memory_order_relaxed); // Track F, F20j (M2 event queue)
»»}
''', where='before', scope=('int KernelEqueuePrivate::TriggerEvent(uintptr_t ident, int16_t filter, void* trigger_data) {', 'static void UserEventTriggerFunc(KernelEqueueEvent* event, void* trigger_data) {'), tag='trigger')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/graphics/presentation/videoOut.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
f.ins('m_presenter.Present(*r.frame);', '''
»»// Track F, F20j (KYTY_DIAG_B32 M3 H:present; stand KYTY_TEST_B32 mode present sleeps inside the mark): one flag.
»»Common::DiagB32::Mark b32;
»»if (Common::DiagB32::g_present_site) [[unlikely]] {
»»»if (Common::DiagB32::g_on) {
»»»»b32.BeginH(Common::DiagB32::Call::Present);
»»»}
»»»Common::DiagB32::TestPresentPoint();
»»}
''', where='before', tag='present-begin')
f.ins('m_presenter.Present(*r.frame);', '''
»»b32.End(0, false);
''', tag='present-end')
f.ins('r.cfg->flip_status.count++;', '''
»// Track F, F20j (KYTY_DIAG_B32): the window boundary for the B32 sampler (n = FrameTrace: n= of this flip); the
»// reports the sampler has closed are printed here, outside m_mutex.
»if (Common::DiagB32::g_on) [[unlikely]] {
»»Common::DiagB32::OnFlip(r.cfg->flip_status.count, r.id, r.reserve_host_ns);
»}
''', scope=('bool FlipQueue::Flip(uint32_t micros) {', 'Graphics::GpuTimeProfiler::SetFrame(static_cast<uint32_t>(r.cfg->flip_status.count));'), tag='flip')
f.ins('return VIDEO_OUT_ERROR_FLIP_QUEUE_FULL;', '''
»}
»if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (M2 flip request): who requested this flip (flip_tid)
»»Common::DiagB32::NoteFlipRequest(request_id, source == FlipRequestSource::Cpu);
''', scope=('static int ReserveFlipRequest(VideoOutDriver::Impl& driver, int handle, int index, int flip_mode,', 'Graphics::ImageInfo BufferAttributeGroup::ImageInfo(const VideoOutBuffer& buffer) const {'), tag='reserve')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/graphics/presentation/window/swapchain.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
SW = ('Swapchain::Status Swapchain::AcquireNextImage(CommandScheduler& scheduler) {', 'EXIT_IF(m_image_index >= m_images.size());')
f.ins('m_image_index     = static_cast<uint32_t>(-1);', '''
»Common::DiagB32::Mark b32; // Track F, F20j (KYTY_DIAG_B32 M3 H:acquire)
»if (Common::DiagB32::g_on) [[unlikely]] {
»»b32.BeginH(Common::DiagB32::Call::Acquire);
»}
''', where='before', scope=SW, tag='acquire-begin')
f.ins('&m_image_index);', '''
»b32.End(0, false);
''', scope=SW, tag='acquire-end')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/graphics/host_gpu/renderer/commandScheduler.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
f.ins('DrainAsyncSubmits();', '''
»Common::DiagB32::Mark b32_drain; // Track F, F20j (KYTY_DIAG_B32 M3 H:drain)
»if (Common::DiagB32::g_on) [[unlikely]] {
»»b32_drain.BeginH(Common::DiagB32::Call::Drain);
»}
''', where='before', scope=('CtxTick::RecordBlock("submit-sync");', 'const auto buffer = m_command.m_buffer;'), tag='drain-begin')
f.ins('DrainAsyncSubmits();', '''
»b32_drain.End(0, false);
''', scope=('CtxTick::RecordBlock("submit-sync");', 'const auto buffer = m_command.m_buffer;'), tag='drain-end')
QS = ('const auto buffer = m_command.m_buffer;', 'if (result != vk::Result::eSuccess) {')
f.ins('Common::LockGuard lock(graphics.queue_mutex);', '''
»»Common::DiagB32::Mark b32_q; // Track F, F20j (KYTY_DIAG_B32 M3 H:qlock - the wait for graphics.queue_mutex)
»»if (Common::DiagB32::g_on) [[unlikely]] {
»»»b32_q.BeginH(Common::DiagB32::Call::QLock);
»»}
''', where='before', scope=QS, tag='qlock-begin')
f.ins('Common::LockGuard lock(graphics.queue_mutex);', '''
»»b32_q.End(0, false);
''', scope=QS, tag='qlock-end')
f.ins('result = graphics.queue.submit(1, &submit_info, nullptr);', '''
»»if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (KYTY_DIAG_B32 M3 H:qsubmit)
»»»b32_q.BeginH(Common::DiagB32::Call::QSubmit);
»»}
''', where='before', scope=QS, tag='qsubmit-begin')
f.ins('result = graphics.queue.submit(1, &submit_info, nullptr);', '''
»»b32_q.End(0, false);
''', scope=QS, tag='qsubmit-end')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/graphics/host_gpu/renderer/masterSemaphore.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
MS = ('void MasterSemaphore::Wait(uint64_t tick) {', 'if (result != vk::Result::eSuccess) {')
f.ins('do {', '''
»»Common::DiagB32::Mark b32; // Track F, F20j (KYTY_DIAG_B32 M3 H:semwait - vkWaitSemaphores)
»»if (Common::DiagB32::g_on) [[unlikely]] {
»»»b32.BeginH(Common::DiagB32::Call::SemWait);
»»}
''', where='before', scope=MS, tag='semwait-begin')
f.ins('} while (diagnostic && result == vk::Result::eTimeout);', '''
»»b32.End(0, false);
''', scope=MS, tag='semwait-end')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/common/platform/sysWindowsVirtual.cpp')
f.ins('DWORD old_protect = 0;', '''
»Common::DiagB32::Mark b32; // Track F, F20j (KYTY_DIAG_B32 M3 H:protect - VirtualProtect, ends with the scope)
»if (Common::DiagB32::g_on) [[unlikely]] {
»»b32.BeginH(Common::DiagB32::Call::Protect);
»}
''', scope=('bool SysVirtualProtect(uint64_t address, uint64_t size, VirtualMemory::Mode mode) {', 'bool SysVirtualFlushInstructionCache(uint64_t address, uint64_t size) {'), tag='protect')
f.save()
f = F('src/common/platform/sysWindowsVirtual.cpp')
f.ins('#include "common/assert.h"', INC, tag='include')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/common/hostException.cpp')
f.ins('const bool resolved = handler(info);', '''
»»Common::DiagB32::Mark b32; // Track F, F20j (KYTY_DIAG_B32 M3 H:fault - the guest exception handler)
»»if (Common::DiagB32::g_on) [[unlikely]] {
»»»b32.BeginH(Common::DiagB32::Call::Fault);
»»}
''', where='before', tag='fault-begin')
f.ins('const bool resolved = handler(info);', '''
»»b32.End(0, false);
''', tag='fault-end')
f.save()
f = F('src/common/hostException.cpp')
f.ins('#include "common/frameStats.h"', INC, tag='include')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/graphics/guest_gpu/graphicsRun.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
f.ins('m_queues[submission.queue_id].push_back(std::move(submission));', '''
»if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (M4): the last guest submission - waker of W:gpu_idle
»»Common::DiagB32::NoteSubmit(submission.bf.seq);
»}
''', where='before', tag='enqueue')
TR = ('void GuestGpu::ThreadRun(void* data) {', 'EXIT_IF(!has_submission);')
f.ins('Submission                   submission;', '''
»»if (Common::DiagB32::g_test_gpusleep) [[unlikely]] { // Track F, F20j: stand KYTY_TEST_B32 gpusleep, outside every mark
»»»Common::DiagB32::TestGpuSleepPoint();
»»}
''', where='before', scope=TR, tag='gpusleep')
f.ins('gpu->m_work_available.Wait(&gpu->m_queue_mutex);', '''
»»»»»Common::DiagB32::Mark b32; // Track F, F20j (KYTY_DIAG_B32 M4 W:gpu_idle; waker - the last guest submission)
»»»»»if (Common::DiagB32::g_on) [[unlikely]] {
»»»»»»b32.BeginW(Common::DiagB32::Wait::GpuIdle, gpu, 0, 0);
»»»»»}
''', where='before', scope=TR, tag='idle-begin')
f.ins('gpu->m_work_available.Wait(&gpu->m_queue_mutex);', '''
»»»»»if (b32.Active()) [[unlikely]] {
»»»»»»b32.End(Common::DiagB32::LastSubmitWaker(b32.SinceNs()), false);
»»»»»}
''', scope=TR, tag='idle-end')
f.ins('gpu->m_work_available.WaitFor(&gpu->m_queue_mutex, 100);', '''
»»»»»»Common::DiagB32::Mark b32; // Track F, F20j (KYTY_DIAG_B32 M4 W:gpu_regmem - all queues on WAIT_REG_MEM)
»»»»»»if (Common::DiagB32::g_on) [[unlikely]] {
»»»»»»»b32.BeginW(Common::DiagB32::Wait::GpuRegmem, gpu, 0, 100000);
»»»»»»}
''', where='before', scope=TR, tag='regmem-begin')
f.ins('gpu->m_work_available.WaitFor(&gpu->m_queue_mutex, 100);', '''
»»»»»»b32.End(0, false);
''', scope=TR, tag='regmem-end')
f.ins('submission  = std::move(queue.front());', '''
»»»»if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j: the submission whose flip packet names flip_tid
»»»»»Common::DiagB32::NoteCurrentSubmission(submission.bf.seq);
»»»»}
''', scope=TR, tag='cur-sub')
f.save()

# ---------------------------------------------------------------------------------------------------------------------
f = F('src/graphics/presentation/window/window.cpp')
f.ins('#include "common/assert.h"', INC, where='before', tag='include')
f.ins('WindowTestHidLossNoteGuestText(text, size); // Track F, F19c, KYTY_TEST_HIDLOSS (item 451(c))', '''
»if (Common::DiagB32::g_test_on && text != nullptr) [[unlikely]] { // Track F, F20j: KYTY_TEST_B32 arms on the same line
»»if (TestMinimizeIsLevelEntry(std::string_view(text, size))) {
»»»Common::DiagB32::TestArm();
»»}
»}
''', tag='arm')
f.save()

f = F('CMakeLists.txt')
f.ins('"${KYTY_TESTS_DIR}/F8AudioStand.cpp")', """

# Track F, F20j (KYTY_DIAG_B32 core: partition, I1, I2', I3, window, lines, counters; ROADMAP s122 item 550(z)(4)):
# run by docs/track-f/f20j/run_tests_f20j.py, not by ctest.
add_executable(diag_b32_tests EXCLUDE_FROM_ALL
»"${KYTY_TESTS_DIR}/DiagB32Tests.cpp"
)
target_link_libraries(diag_b32_tests common fmt::fmt)
target_include_directories(diag_b32_tests PRIVATE ${inc_headers})
""", tag='test target')
f.save()

for d in done:
    print('OK ', d)
for x in fails:
    print('FAIL', x)
print('ALL OK' if not fails else 'FAILED %d' % len(fails))
sys.exit(0 if not fails else 1)
