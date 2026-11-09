# Whole vehicles, trims/tiers and model numbers

## Tier naming - use the manufacturer's own word, exactly
Find what the maker calls its levels and put it in `tiers.json` -> `tier_label`, and use their spelling for
every tier/package/option. Examples: Toyota "Grade" (2010 Tundra: Tundra grade, Limited grade + SR5 /
Work Truck / TRD / Platinum *packages*); Ford "series" / "trim" + package codes (e.g. 302A); GM "trim" + RPO
codes; Honda "trim"; John Deere "Series" (100, X300 Select Series...); Cub Cadet "Series" (XT1 Enduro);
Husqvarna model families; Stihl/Milwaukee model numbers; boats "package"; appliances "series".
Check the brochure / order guide / price list for the year: they list every package and option code.

## Model numbers in everything
- `set.model_no` (sheets.json), `sheet.model_no` (panel.json), `identity.model_no` (model.json), `meta.model_no`
  (doc.json) - all the same string. It prints top-right on every sheet, in the title block (yellow), on the
  manual cover and page headers, in file names, CAD properties and BOM rows.
- Tiers: put each tier's maker model / trim code in `tiers[].code` (VIN decode, order guide, window sticker);
  options: `features[].code` (package / RPO / option code). Parts: `part_no` on every part.
- Unknown? write "by VIN" / "See maker parts list" - never invent a number.

## tiers.json
```
{"tier_label":"Grade","family":"2010 Toyota Tundra","note":"...",
 "tiers":[{"name":"Tundra Grade Double Cab","code":"..."}, ...],          # <= 7 per sheet panel; more -> split
 "groups":[{"group":"Packages","features":[{"feature":"SR5 Package","code":"","values":["O","O",...]}]}]}
```
Values: S standard · O optional · P part of a package · - not available · any other short text (e.g. a code,
"V" = verify) prints in the cell. One value per tier (check_specs enforces it).

## Whole-vehicle package (machine_class: car / truck / suv / van / motorcycle / atv / utv)
Sheets (key sheet is automatic): 1 multi-view (side elevation, plan, end view) with build dimensions table
(L, W, H by drivetrain, wheelbase(s), track, ground clearance, approach/departure, bed/cargo, fuel) ·
2 isometric · 3+ trim/package/option matrix (split by group if long) · powertrain variants (engine codes,
outputs, transmissions) · electrical: power distribution / fuses & relays, starting & charging, lighting,
body/accessory circuits, added circuits · interior/dashboard (blank switches per tier = panel.json preset) ·
chassis (suspension, brakes, steering) · service data (fluids, capacities, torque, intervals) · towing/payload
by configuration · parts index. Cabs/beds/drivetrains that change dimensions: give each its own row or sheet.
Manual: split into volumes when long (`doc-1-overview.json`, `doc-2-service.json`, `doc-3-electrical.json`);
each becomes its own PDF.
Research: VIN decode (vPIC), brochure + order guide for the year, window-sticker decoders, EPC parts catalogs,
TSBs, owner forums for poverty buttons.
