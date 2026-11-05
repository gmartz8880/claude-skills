# TI-84 Plus CE reference (TI-BASIC + C)

## TI-BASIC getKey codes
| Key | Code | Key | Code | Key | Code |
|---|---|---|---|---|---|
| Y= | 11 | window | 12 | zoom | 13 |
| trace | 14 | graph | 15 | 2nd | 21 |
| mode | 22 | del | 23 | left | 24 |
| up | 25 | right | 26 | alpha | 31 |
| X,T,θ,n | 32 | stat | 33 | down | 34 |
| math | 41 | apps | 42 | prgm | 43 |
| vars | 44 | clear | 45 | x⁻¹ | 51 |
| sin | 52 | cos | 53 | tan | 54 |
| ^ | 55 | x² | 61 | , | 62 |
| ( | 63 | ) | 64 | ÷ | 65 |
| log | 71 | 7 | 72 | 8 | 73 |
| 9 | 74 | × | 75 | ln | 81 |
| 4 | 82 | 5 | 83 | 6 | 84 |
| − | 85 | sto→ | 91 | 1 | 92 |
| 2 | 93 | 3 | 94 | + | 95 |
| 0 | 102 | . | 103 | (−) | 104 |
| enter | 105 | on | (breaks the program) | | |

## TI-BASIC source text rules (for `build.py`, tokenized by tivars)
- One command per line (or `:` separated). Use the real symbols: `→ ≠ ≤ ≥ ² ⁻¹ √( ∟ θ`. `π` is converted automatically.
- Closing quotes/parentheses at line end may be omitted (saves bytes), but keep them in inner expressions.
- Comments: a line that is just a string `"LIKE THIS` (costs a few bytes; keep them short).
- Program name: 1-8 chars, A-Z 0-9 (θ allowed), first char a letter.
- Useful commands: `ClrHome Disp Output( Input Prompt Pause Menu( getKey Wait If Then Else End For( While
  Repeat Lbl Goto Return Stop DelVar StoreGDB RecallGDB Text( Line( Pt-On( TextColor( BackgroundOn
  round( int( iPart( fPart( solve( nDeriv( fnInt( toString( eval( sub( length( inString(`

## C toolchain essentials (CEdev)
| Need | Call |
|---|---|
| Graphics start / end | `gfx_Begin()` / `gfx_End()` |
| Double buffer | `gfx_SetDrawBuffer()`, `gfx_SwapDraw()`, `gfx_Wait()` |
| Draw | `gfx_FillScreen(c)` `gfx_SetColor(c)` `gfx_FillRectangle(x,y,w,h)` `gfx_Rectangle` `gfx_Line` `gfx_Circle` |
| Text | `gfx_PrintStringXY(s,x,y)` `gfx_SetTextFGColor` `gfx_SetTextBGColor` `gfx_SetTextScale(w,h)` |
| Keys | `kb_SetMode(MODE_3_CONTINUOUS)` then read `kb_Data[group] & kb_Key`, or `kb_Scan()`; `kb_AnyKey()`; `kb_Reset()` |
| Key groups | g1: kb_Graph kb_Trace kb_Zoom kb_Window kb_Yequ kb_2nd kb_Mode kb_Del; g6: kb_Enter kb_Add kb_Sub kb_Mul kb_Div kb_Power kb_Clear; g7: kb_Down kb_Left kb_Right kb_Up |
| Files | `ti_Open(name,"r"/"w"/"a")` (0 = fail) `ti_Read` `ti_Write` `ti_SetArchiveStatus(true,h)` `ti_Close` |
| Timing | `delay(ms)`, `clock()` with `CLOCKS_PER_SEC` (32768) |
| Power | `boot_GetBatteryStatus()` (0-4), `boot_BatteryCharging()`, `lcd_BacklightLevel` (0 bright - 255 dark), `boot_Set6MHzMode()` / `boot_Set48MHzMode()` |
| Screen size | `GFX_LCD_WIDTH` 320, `GFX_LCD_HEIGHT` 240 |

makefile keys: `NAME` (<= 8 chars), `ICON` (16x16 png), `DESCRIPTION`, `COMPRESSED = YES`, `ARCHIVED = YES`,
`CFLAGS = -Wall -Wextra -Oz`, last line `include $(shell cedev-config --makefile)`.

Users must send `clibs.8xg` once (graphx/keypadc/fileioc), from CE-Programming/libraries releases.
