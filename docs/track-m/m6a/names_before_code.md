# M6a (HPP-848) — имена строк и полей до кода (п. 767(в), (з), (и))

Записано до первой правки кода (время — `times.txt`).

## Ручка и строки ручки (только при `KYTY_DIAG_M5W2=1`, умолчание 0)
- `M5W2: mode=<0|1>` — один раз на процесс при первом чтении ручки.
- `M5W2Stat: when=<periodic|exit> ao_obj_push= ao_obj_nz= ao_obj_nopcm= ao_bus_push= ao_bus_nz= clr_dw= clr_dw_div= minlod_views= minlod_div= inv_calls= inv_part= inv_gpu= inv_off= raw_rd= raw_rd_gpu=`
  (поля п. 767(и) плюс справочные `ao_obj_nopcm`, `ao_bus_push`, `inv_gpu`, `inv_off`).
- `M5W2Clr: when=<periodic|exit> fmt=<vk::Format число> clr_dw= clr_dw_div=` — по строке на формат с `clr_dw` > 0 (поле «по формату»).
- `periodic` — каждые 4 096 Push AudioOut2 (`AudioOut2ContextPush` с постановкой в очередь), `exit` — оба выхода `Execute` (`emulator.cpp`).

## Строки без ручки (вне набора подписи)
- T031: `GuestPrintf: negative precision prec=<p>` — раз на процесс.
- T309: `AmprRecordSpace: refused why=<arg|header|buffer|space|backing> cb=0x.. record_size=0x.. write_offset=0x.. size=0x.. n=<k>` — отказ `EnsureCommandBufferRecordSpace`, предел 20.
- T309: `AmprWriteAddress: refused why=<state|ensure> cb=0x.. record_size=0x.. address=0x.. value=0x.. n=<k>` — отказ `AppendWriteAddressRecord`, предел 20.
- T023: `AgcReserveDW: cursor state class=<up0|down0|both0|down_lt_up> up=0x.. down=0x.. reserved_dw= num_dw= callback=<0|1> n=<k>` — вход `ReserveDW`, предел 20.
