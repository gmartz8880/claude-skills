/*
 * TI-84 Plus CE app skeleton (CE C/C++ Toolchain v13+)
 * Built for: battery life, stability, and a snappy feel.
 *
 *  Battery   - redraw only when something changed (dirty flag), idle backlight dim,
 *              idle auto-save + exit (mirrors the OS auto power down), optional 6 MHz idle mode.
 *  Stability - every resource is restored on exit (backlight, CPU speed, graphx, keypad),
 *              settings are versioned + checksummed, all file I/O is checked.
 *  Snappy    - double buffering (no flicker), input read every loop, no blocking work on the
 *              UI path, instant response on the first key press.
 *
 * Controls: arrows move, [enter]/[2nd] select, [mode] help, [clear]/[del] back, [clear] on menu quits.
 */
#include <graphx.h>
#include <keypadc.h>
#include <fileioc.h>
#include <sys/timers.h>
#include <sys/power.h>
#include <sys/lcd.h>
#include <time.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* ---------------- configuration ---------------- */
#define APP_TITLE        "My CE App"
#define APP_VERSION      "1.0"
#define CFG_APPVAR       "MYAPPCFG"   /* <= 8 chars, unique per app */
#define CFG_VERSION      1
#define IDLE_DIM_SEC     20           /* dim backlight after this many idle seconds */
#define IDLE_EXIT_SEC    240          /* auto-save and exit after this many idle seconds (~OS APD) */
#define LOOP_IDLE_MS     30           /* rest between key checks when nothing is happening */
#define USE_6MHZ_IDLE    0            /* 1 = drop CPU to 6 MHz while dimmed (test on hardware first) */
#define DIM_LEVEL        200          /* 0 = brightest, 255 = darkest */

/* ---------------- persistent settings ---------------- */
typedef struct {
    uint8_t version;
    uint8_t dark_mode;
    uint8_t last_item;
    uint16_t checksum;
} config_t;

static config_t cfg;

static uint16_t cfg_sum(const config_t *c) {
    const uint8_t *p = (const uint8_t *)c;
    uint16_t s = 0x5A5A;
    for (size_t i = 0; i < offsetof(config_t, checksum); i++) s = (uint16_t)((s << 1) ^ p[i]);
    return s;
}

static void cfg_defaults(void) {
    memset(&cfg, 0, sizeof cfg);
    cfg.version = CFG_VERSION;
}

static void cfg_load(void) {
    config_t tmp;
    uint8_t h = ti_Open(CFG_APPVAR, "r");
    cfg_defaults();
    if (!h) return;
    if (ti_Read(&tmp, sizeof tmp, 1, h) == 1 && tmp.version == CFG_VERSION && tmp.checksum == cfg_sum(&tmp))
        cfg = tmp;                       /* only accept valid, current-version data */
    ti_Close(h);
}

static bool cfg_save(void) {
    bool ok;
    uint8_t h;
    cfg.checksum = cfg_sum(&cfg);
    h = ti_Open(CFG_APPVAR, "w");
    if (!h) return false;
    ok = ti_Write(&cfg, sizeof cfg, 1, h) == 1;
    ti_SetArchiveStatus(true, h);        /* archived = survives RAM resets */
    ti_Close(h);
    return ok;
}

/* ---------------- app state ---------------- */
enum screen { SCR_MENU, SCR_MAIN, SCR_HELP, SCR_ABOUT };
static const char *menu_items[] = { "Start", "Dark mode", "Help", "About", "Quit" };
#define MENU_COUNT ((uint8_t)(sizeof menu_items / sizeof *menu_items))

static enum screen scr = SCR_MENU;
static uint8_t sel = 0;
static bool dirty = true;
static uint8_t saved_backlight;
static bool dimmed = false;

static uint8_t fg(void) { return cfg.dark_mode ? 255 : 0; }
static uint8_t bg(void) { return cfg.dark_mode ? 0 : 255; }

static void header(const char *t) {
    uint8_t bar = cfg.dark_mode ? 74 : 24;
    uint8_t b = boot_GetBatteryStatus();  /* 0..4 */
    if (b > 4) b = 4;
    gfx_SetColor(bar);
    gfx_FillRectangle_NoClip(0, 0, GFX_LCD_WIDTH, 18);
    gfx_SetTextFGColor(255);
    gfx_SetTextBGColor(bar);
    gfx_PrintStringXY(t, 4, 5);
    gfx_SetColor(255);
    gfx_Rectangle_NoClip(GFX_LCD_WIDTH - 30, 4, 24, 10);
    gfx_FillRectangle_NoClip(GFX_LCD_WIDTH - 28, 6, (uint8_t)(b * 5), 6);
    gfx_SetTextFGColor(fg());
    gfx_SetTextBGColor(bg());
}

static void draw(void) {
    uint8_t i;
    gfx_FillScreen(bg());
    switch (scr) {
    case SCR_MENU:
        header(APP_TITLE);
        for (i = 0; i < MENU_COUNT; i++) {
            int y = 30 + i * 16;
            uint8_t hi = cfg.dark_mode ? 107 : 222;
            if (i == sel) { gfx_SetColor(hi); gfx_FillRectangle_NoClip(0, y - 3, GFX_LCD_WIDTH, 14); }
            gfx_SetTextBGColor(i == sel ? hi : bg());
            gfx_PrintStringXY(menu_items[i], 12, y);
            if (i == 1) gfx_PrintString(cfg.dark_mode ? " [on]" : " [off]");
        }
        gfx_SetTextBGColor(bg());
        gfx_PrintStringXY("[mode] help   [clear] quit", 4, GFX_LCD_HEIGHT - 12);
        break;
    case SCR_MAIN:
        header("Main");
        gfx_PrintStringXY("Your app runs here.", 8, 30);
        gfx_PrintStringXY("[clear] back", 4, GFX_LCD_HEIGHT - 12);
        break;
    case SCR_HELP:
        header("Help");
        gfx_PrintStringXY("Arrows: move   Enter/2nd: select", 8, 30);
        gfx_PrintStringXY("Mode: help     Clear/Del: back", 8, 46);
        gfx_PrintStringXY("Settings save automatically.", 8, 62);
        break;
    case SCR_ABOUT:
        header("About");
        gfx_PrintStringXY(APP_TITLE " v" APP_VERSION, 8, 30);
        gfx_PrintStringXY("Built with the CE C toolchain.", 8, 46);
        break;
    }
    gfx_SwapDraw();                      /* show the finished frame: no flicker */
    dirty = false;
}

static void wake(void) {
    if (dimmed) { lcd_BacklightLevel = saved_backlight; dimmed = false; }
#if USE_6MHZ_IDLE
    boot_Set48MHzMode();
#endif
}

/* returns false when the app should quit */
static bool handle_keys(void) {
    static kb_key_t prev7 = 0, prev1 = 0, prev6 = 0;
    kb_key_t g7 = kb_Data[7], g1 = kb_Data[1], g6 = kb_Data[6];
    kb_key_t n7 = g7 & ~prev7, n1 = g1 & ~prev1, n6 = g6 & ~prev6;   /* new presses only */
    bool back, ok;
    prev7 = g7; prev1 = g1; prev6 = g6;
    if (!(n7 | n1 | n6)) return true;

    back = (n6 & kb_Clear) || (n1 & kb_Del);
    ok = (n6 & kb_Enter) || (n1 & kb_2nd);
    if (n1 & kb_Mode) { scr = SCR_HELP; dirty = true; return true; }

    if (scr == SCR_MENU) {
        if (n7 & kb_Up)   { sel = sel ? sel - 1 : MENU_COUNT - 1; dirty = true; }
        if (n7 & kb_Down) { sel = (uint8_t)((sel + 1) % MENU_COUNT); dirty = true; }
        if (back) return false;
        if (ok) {
            dirty = true;
            switch (sel) {
            case 0: scr = SCR_MAIN; break;
            case 1: cfg.dark_mode ^= 1; cfg_save(); break;
            case 2: scr = SCR_HELP; break;
            case 3: scr = SCR_ABOUT; break;
            default: return false;
            }
        }
    } else if (back) { scr = SCR_MENU; dirty = true; }
    return true;
}

int main(void) {
    clock_t last_input;
    bool running = true;

    cfg_load();
    sel = cfg.last_item < MENU_COUNT ? cfg.last_item : 0;
    saved_backlight = lcd_BacklightLevel;

    gfx_Begin();
    gfx_SetDrawBuffer();
    kb_SetMode(MODE_3_CONTINUOUS);       /* hardware keeps kb_Data fresh; no blocking scans */

    last_input = clock();
    while (running) {
        if (kb_AnyKey()) {
            last_input = clock();
            if (dimmed) { wake(); dirty = true; }
            running = handle_keys();
        } else {
            unsigned long idle;
            handle_keys();               /* keep edge detection in sync on release */
            idle = (unsigned long)((clock() - last_input) / CLOCKS_PER_SEC);
            if (!dimmed && idle >= IDLE_DIM_SEC) {
                lcd_BacklightLevel = DIM_LEVEL;
                dimmed = true;
#if USE_6MHZ_IDLE
                boot_Set6MHzMode();
#endif
            }
            if (idle >= IDLE_EXIT_SEC) running = false;    /* save battery like the OS APD */
            if (!dirty) delay(LOOP_IDLE_MS);               /* rest between key checks */
        }
        if (dirty && running) draw();
    }

    cfg.last_item = sel;
    cfg_save();
    wake();                              /* restore backlight + CPU speed */
    kb_SetMode(MODE_0_IDLE);
    kb_Reset();
    gfx_End();                           /* restores the OS screen mode */
    return 0;
}
