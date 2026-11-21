"""Round 27, checker A: one line per view from ../logs/views.json -> ../logs/views.txt"""
import json, os
import drive as D

v = json.load(open(os.path.join(D.LOGS, 'views.json'), encoding='utf-8'))
lines = []
for name, r in v.items():
    if 'holes' not in r:
        lines.append('%s: %s' % (name, r.get('error', '?'))); continue
    c = r['cam']
    lost = r['balls_by_radius_seen_and_fully_lost']
    lines.append(
        '%-15s grid %d t %g, %d rounds, eye %.2f from (%.3f, %.1f, %.1f), picks every %d px (%d) | reference: %d balls, hits %d, complete to 0.2 px at %.0f%% of its hits | '
        'lab stops %d | HOLES (reference hits, lab does not stop): %d points, widest %.0f px, longest chord %.2f px | PASSED THROUGH (lab stops > 1 px behind): %d, longest chord %.2f px | '
        'balls lost (>= half of >= 3 points): %d of %d, largest %.1f px across | balls fully lost by radius: %s | '
        'EXTRA stops (lab stops, reference ray misses): %d points, at most %.2f px from a real ball | lab stopping points: median %.2f px off the nearest ball, 99%% within %.2f, most %.2f; more than 2 px off: %d points (widest blob %.0f px, most %.1f px); deepest inside a ball %.2f px | '
        'colour more than 3 px outside the reference: %d px (widest %.0f px) | grid points left out (reference not complete there): %d | reference holds balls of radius >= %g px | '
        'the points more than 2 px off, probed with the recipe: a real ball within 2 px at %d, solid only by the depth of the search at %d (widest blob %.0f px), stopped in the open at %d (widest blob %.0f px)'
        % (name, r['grid'], r['t'], r['rounds'], c['dist'], c['target'][0], c['target'][1], c['target'][2], r['pick_step'], r['picks'], r['balls'], r['ref_hits'], 100 * r['ref_complete_share'],
           r['lab_stops'], r['holes']['points'], r['holes']['widest_px'], r['holes']['weight_max'], r['behind']['points'], r['behind']['weight_max'],
           r['balls_missing'], r['balls_seen_on_3_points_or_more'], r['largest_missing_ball_diameter_px'],
           ', '.join('%s: %d of %d' % (k, b, a) for k, (a, b) in lost.items()),
           r['extra']['points'], r['extra']['weight_max'], r['float_median_px'], r['float_p99_px'], r['float_max_px'],
           r['floating_over_2px']['points'], r['floating_over_2px']['widest_px'], r['floating_over_2px']['weight_max'], r['deepest_inside_a_ball_px'],
           r['colour_added_over_3px_outside'], r['colour_added_over_3px_outside_widest_px'], r['outside_complete_zone'], r.get('min_radius_px', 0.2),
           r.get('far_points', {}).get('a_real_ball_within_2px', 0), r.get('far_points', {}).get('only_the_depth_puts_solid_there', 0), r.get('solid_by_depth_only', {}).get('widest_px', 0),
           r.get('far_points', {}).get('nothing_there', 0), r.get('stopped_in_the_open', {}).get('widest_px', 0)))
with open(os.path.join(D.LOGS, 'views.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines))
