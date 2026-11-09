# Technical Manual outline - the "comprehensive" standard

A manual counts as comprehensive when a competent owner could operate, maintain, troubleshoot and repair the
machine with it plus normal tools. Use these sections (skip only what truly does not apply; say why):

1. **Scope & applicability** - exact machine, model/serial/VIN range, what is and isn't covered, "verify" note.
2. **Safety** - hazards specific to the machine (energy sources: electrical, hydraulic, stored spring/pressure,
   rotating parts, heat, fuel, CO, airbags/SRS, batteries). Lockout/tagout steps (OSHA 29 CFR 1910.147 where
   relevant), PPE, disposal. CAUTION boxes are red and placed BEFORE the step they protect.
3. **Description & theory of operation** - how it works, in plain words, with a block/flow figure.
4. **Specifications** - weights, capacities, ratings, fluids, electrical data. Mark typical vs verified.
4A. **Physical build dimensions** - table of overall and mounting dimensions with "where shown" (sheet/view),
    clearances for cooling/service, and a note to measure before fabrication.
5. **Component identification** - callout table matching the drawings.
5A. **Electrical system** - how the circuits work (refer to the schematic sheet by number), wire table,
    connector/fuse/relay locations, and electrical test procedures (voltage drop, continuity, no-start tests).
6. **Controls & instruments** - every control and what it does (poverty buttons / options when relevant).
7. **Tools, consumables & special tools.**
8. **Operation** - pre-use checks, start, run, stop, storage.
9. **Maintenance schedule** - interval table.
10. **Service & adjustment procedures** - one `procedure` block each: purpose, tools, caution, numbered steps,
    torque/spec values inline, verification. Aim for every routine task + common repairs.
11. **Troubleshooting** - symptom / likely cause / check-fix table (8+ rows for complex machines).
12. **Upgrades, options & retrofits** - including factory blanks/poverty buttons: OEM route, aftermarket route,
    difficulty, wiring figure.
13. **Parts list** - item, description, part no., qty, source, price/date checked; "verify by serial/VIN".
14. **Drawing appendix** - `{"sheets": {...}}` block (every sheet, full page).
15. **References & revision history** - sources with dates.

Writing style: plain words, imperative steps, one action per step, units always, no fluff. Legibility first.
