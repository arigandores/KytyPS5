"""S17a2 (HPP-618, ROADMAP s122 item 532(g)), second edit: ShaderTranslationCache::Signature() already ends with its own
newline (shaderTranslationCache.cpp: m_signature = ... + variant + newline), so the S17a header line was terminated and the
first edit of patch_s17a2.py gave an empty line after it. The header is made one line by construction: trailing CR/LF of
the signature cut, one newline added (for the current signature the bytes equal the S17a form). Whole-line anchors, LF.
Usage: python patch_s17a2_rc3.py <KytyPS5 root>"""
import sys

ROOT = sys.argv[1].rstrip('/') + '/'
REL = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
OLD = r'''		std::string manifest = fmt::format("# ShaderReplay rebuild manifest; signature {}\n", cache.Signature());'''
NEW = r'''		// S17a2 (item 532(g), RC3 of the S17b review): Signature() ends with its own newline (shaderTranslationCache.cpp);
		// the header is one line by construction - trailing CR/LF of the signature cut, one newline added.
		std::string signature = cache.Signature();
		while (!signature.empty() && (signature.back() == '\n' || signature.back() == '\r')) {
			signature.pop_back();
		}
		std::string manifest = fmt::format("# ShaderReplay rebuild manifest; signature {}\n", signature);'''

path = ROOT + REL
text = open(path, 'rb').read().decode('utf-8')
assert '\r\n' not in text
lines = text.split('\n')
hits = [i for i, l in enumerate(lines) if l == OLD]
if len(hits) != 1:
    sys.exit('ANCHOR FAIL (%d hits)' % len(hits))
lines[hits[0]:hits[0] + 1] = NEW.split('\n')
open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
print('patched', REL, 'line', hits[0] + 1)
