/**
 * workout_animations.js
 * SVG stick-figure animations for each exercise.
 * 
 * Each animation is a function that draws into a <svg> element
 * using requestAnimationFrame, looping continuously while active.
 * 
 * Public API:
 *   WorkoutAnim.show(exerciseName)  — start animation
 *   WorkoutAnim.stop()              — stop & clear
 */

const WorkoutAnim = (() => {

  let _raf = null;
  let _svg = null;
  let _t   = 0;

  // ── SVG helpers ────────────────────────────────────────────────────────────
  const NS = 'http://www.w3.org/2000/svg';

  function el(tag, attrs) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    return e;
  }

  function line(x1, y1, x2, y2, stroke='#222', w=3) {
    return el('line', { x1, y1, x2, y2, stroke, 'stroke-width': w, 'stroke-linecap': 'round' });
  }

  function circle(cx, cy, r, fill='#222', stroke='none') {
    return el('circle', { cx, cy, r, fill, stroke });
  }

  function clear() {
    while (_svg.firstChild) _svg.removeChild(_svg.firstChild);
  }

  // ── Normalised time (0→1 cycling) ─────────────────────────────────────────
  // speed: cycles per second
  function phase(speed = 0.6) {
    return (_t * speed) % 1;
  }

  // Smooth oscillation between a and b
  function osc(a, b, p) {
    return a + (b - a) * (0.5 - 0.5 * Math.cos(p * 2 * Math.PI));
  }

  // ── Common body measurements (standing centre = cx=100,cy=200) ─────────────
  // HEAD top ~y=30, feet ~y=190
  // Segments: head r=14, neck 44→58, torso 58→105,
  //           upper arm ~30px, forearm ~28px
  //           thigh ~42px, shin ~40px

  function drawHead(cx, cy) {
    _svg.appendChild(circle(cx, cy, 14, 'none', '#222'));
    _svg.appendChild(el('circle', { cx, cy, r: 14, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
  }

  // standing figure, arms/legs parametric
  function standing({
    cx = 100, headY = 44,
    // torso
    neckY, hipY,
    // left/right shoulder, elbow, hand
    lSh, lEl, lHa,
    rSh, rEl, rHa,
    // left/right hip, knee, foot
    lHi, lKn, lFo,
    rHi, rKn, rFo,
  }) {
    neckY = neckY ?? headY + 18;
    hipY  = hipY  ?? neckY + 47;

    // defaults: neutral standing
    lSh = lSh ?? { x: cx - 18, y: neckY + 6 };
    rSh = rSh ?? { x: cx + 18, y: neckY + 6 };
    lEl = lEl ?? { x: cx - 22, y: neckY + 32 };
    rEl = rEl ?? { x: cx + 22, y: neckY + 32 };
    lHa = lHa ?? { x: cx - 22, y: neckY + 56 };
    rHa = rHa ?? { x: cx + 22, y: neckY + 56 };
    lHi = lHi ?? { x: cx - 12, y: hipY };
    rHi = rHi ?? { x: cx + 12, y: hipY };
    lKn = lKn ?? { x: cx - 14, y: hipY + 42 };
    rKn = rKn ?? { x: cx + 14, y: hipY + 42 };
    lFo = lFo ?? { x: cx - 16, y: hipY + 82 };
    rFo = rFo ?? { x: cx + 16, y: hipY + 82 };

    // head + neck + torso + hips
    drawHead(cx, headY);
    _svg.appendChild(line(cx, headY + 14, cx, neckY));      // neck
    _svg.appendChild(line(cx, neckY, cx, hipY));             // torso
    _svg.appendChild(line(lHi.x, lHi.y, rHi.x, rHi.y));    // hips

    // arms
    _svg.appendChild(line(lSh.x, lSh.y, lEl.x, lEl.y));
    _svg.appendChild(line(lEl.x, lEl.y, lHa.x, lHa.y));
    _svg.appendChild(line(rSh.x, rSh.y, rEl.x, rEl.y));
    _svg.appendChild(line(rEl.x, rEl.y, rHa.x, rHa.y));

    // legs
    _svg.appendChild(line(lHi.x, lHi.y, lKn.x, lKn.y));
    _svg.appendChild(line(lKn.x, lKn.y, lFo.x, lFo.y));
    _svg.appendChild(line(rHi.x, rHi.y, rKn.x, rKn.y));
    _svg.appendChild(line(rKn.x, rKn.y, rFo.x, rFo.y));
  }

  // ── ANIMATION LIBRARY ──────────────────────────────────────────────────────

  const animations = {};

  // helper to register
  function reg(names, fn) {
    const arr = Array.isArray(names) ? names : [names];
    arr.forEach(n => { animations[n.toLowerCase()] = fn; });
  }

  // ── Push-ups ───────────────────────────────────────────────────────────────
  reg(['push-ups', 'push ups', 'wide grip push-ups', 'narrow push-ups',
       'diamond push-ups', 'pike push-ups', 'hindu push-ups',
       'airplane push-ups', 'wave push-ups', 'pseudo push-ups',
       'narrow grip kneeling push-ups', 'single leg push-ups (left)',
       'single leg push-ups (right)', 'reverse plank triceps dips',
       'walkouts to push-ups'], () => {
    const p = phase(0.5);
    // Prone plank position — body horizontal, arms pump
    const armAngle = osc(0, 30, p); // degrees down
    const bodyY    = osc(130, 145, p);
    const cx = 100;
    // head
    _svg.appendChild(circle(cx - 52, bodyY - 4, 12, 'none'));
    _svg.appendChild(el('circle', { cx: cx - 52, cy: bodyY - 4, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    // body line
    _svg.appendChild(line(cx - 40, bodyY, cx + 42, bodyY));
    // arms (hands on floor)
    const handY = 165;
    const elbowY = osc(155, 165, p);
    _svg.appendChild(line(cx - 22, bodyY, cx - 28, elbowY));
    _svg.appendChild(line(cx - 28, elbowY, cx - 24, handY));
    _svg.appendChild(line(cx + 4, bodyY, cx + 10, elbowY));
    _svg.appendChild(line(cx + 10, elbowY, cx + 6, handY));
    // legs
    _svg.appendChild(line(cx + 42, bodyY, cx + 50, bodyY + 4));
    _svg.appendChild(line(cx + 50, bodyY + 4, cx + 58, handY));
  });

  // ── Squat family ──────────────────────────────────────────────────────────
  reg(['prisoner squat', 'squat', 'squat jumps', 'squat to walkout',
       'sumo squats', 'half squat walk', 'side step squat',
       'wall sit', 'jump plank'], () => {
    const p = phase(0.5);
    const hipY  = osc(105, 135, p);
    const kneeY = osc(140, 165, p);
    const cx = 100;
    standing({
      cx, headY: 40,
      hipY,
      neckY: 62,
      lHi: { x: cx - 14, y: hipY },
      rHi: { x: cx + 14, y: hipY },
      lKn: { x: cx - 22, y: kneeY },
      rKn: { x: cx + 22, y: kneeY },
      lFo: { x: cx - 18, y: 185 },
      rFo: { x: cx + 18, y: 185 },
      // arms up (prisoner)
      lSh: { x: cx - 18, y: 68 },
      lEl: { x: cx - 30, y: 52 },
      lHa: { x: cx - 20, y: 42 },
      rSh: { x: cx + 18, y: 68 },
      rEl: { x: cx + 30, y: 52 },
      rHa: { x: cx + 20, y: 42 },
    });
  });

  // ── Lunge family ──────────────────────────────────────────────────────────
  reg(['curtsey lunges (left)', 'curtsey lunges (right)',
       'backward lunges (left)', 'backward lunges (right',
       'side lunges (left)', 'side lunges (right)',
       'alternating forward lunges', 'pivot lunge (left)', 'pivot lunge (right)',
       'deep side to side lunge', 'side to side lunge',
       'lunge with internal rotation (left)', 'lunge with internal rotation (right)',
       'lunge with thoracic rotation (left)', 'lunge with thoracic rotation (right)'], () => {
    const p = phase(0.5);
    const cx = 100;
    const frontKneeY = osc(145, 165, p);
    const backKneeY  = osc(155, 170, p);
    standing({
      cx, headY: 38, neckY: 58, hipY: 100,
      lHi: { x: cx - 10, y: 100 },
      rHi: { x: cx + 10, y: 100 },
      lKn: { x: cx - 30, y: frontKneeY },
      rKn: { x: cx + 18, y: backKneeY },
      lFo: { x: cx - 38, y: 185 },
      rFo: { x: cx + 20, y: 185 },
    });
  });

  // ── Mountain climber ──────────────────────────────────────────────────────
  reg(['mountain climber', 'mountain climbers',
       'modified diagonal mountain climbers',
       'mountain climber - to push-ups'], () => {
    const p = phase(0.8);
    const cx = 100;
    // plank, alternating knee drive
    const lKneeX = osc(cx + 10, cx - 10, p);
    const lKneeY = osc(155, 135, p);
    const rKneeX = osc(cx - 10, cx + 10, p);
    const rKneeY = osc(135, 155, p);
    // body
    _svg.appendChild(el('circle', { cx: cx - 52, cy: 128, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx - 40, 132, cx + 38, 132));
    // arms
    _svg.appendChild(line(cx - 18, 132, cx - 22, 152));
    _svg.appendChild(line(cx - 22, 152, cx - 20, 165));
    _svg.appendChild(line(cx + 8, 132, cx + 12, 152));
    _svg.appendChild(line(cx + 12, 152, cx + 10, 165));
    // legs
    _svg.appendChild(line(cx + 38, 132, lKneeX, lKneeY));
    _svg.appendChild(line(lKneeX, lKneeY, lKneeX + 2, 165));
    _svg.appendChild(line(cx + 38, 132, rKneeX, rKneeY));
    _svg.appendChild(line(rKneeX, rKneeY, rKneeX + 4, 165));
  });

  // ── Burpee ────────────────────────────────────────────────────────────────
  reg(['burpee', 'burpees witout jump', 'burpee walk (jumps)'], () => {
    const p = phase(0.35);
    const cx = 100;
    if (p < 0.33) {
      // standing
      const pp = p / 0.33;
      standing({ cx, headY: 38 });
    } else if (p < 0.66) {
      // plank
      _svg.appendChild(el('circle', { cx: cx - 52, cy: 130, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
      _svg.appendChild(line(cx - 40, 133, cx + 42, 133));
      _svg.appendChild(line(cx - 18, 133, cx - 22, 158));
      _svg.appendChild(line(cx - 22, 158, cx - 20, 165));
      _svg.appendChild(line(cx + 8, 133, cx + 12, 158));
      _svg.appendChild(line(cx + 12, 158, cx + 10, 165));
      _svg.appendChild(line(cx + 42, 133, cx + 46, 155));
      _svg.appendChild(line(cx + 46, 155, cx + 48, 165));
    } else {
      // jump up — arms raised
      const jY = osc(38, 28, (p - 0.66) / 0.34);
      standing({
        cx, headY: jY,
        lSh: { x: cx - 18, y: jY + 30 },
        lEl: { x: cx - 32, y: jY + 16 },
        lHa: { x: cx - 26, y: jY + 6 },
        rSh: { x: cx + 18, y: jY + 30 },
        rEl: { x: cx + 32, y: jY + 16 },
        rHa: { x: cx + 26, y: jY + 6 },
      });
    }
  });

  // ── Superman / back bow / backrise ────────────────────────────────────────
  reg(['superman', 'superman - pulls', 'superman rows',
       'back bow with heel taps', 'backrise '], () => {
    const p = phase(0.4);
    const cx = 100;
    const lift = osc(0, 18, p);
    // prone, chest/legs lift
    _svg.appendChild(el('circle', { cx: cx - 36, cy: 148 - lift / 2, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx - 24, 150 - lift / 2, cx + 40, 150));
    // arms forward
    _svg.appendChild(line(cx - 24, 150 - lift / 2, cx - 44, 148 - lift));
    _svg.appendChild(line(cx - 44, 148 - lift, cx - 58, 146 - lift));
    // legs lift
    _svg.appendChild(line(cx + 40, 150, cx + 52, 152 - lift / 2));
    _svg.appendChild(line(cx + 52, 152 - lift / 2, cx + 60, 150 - lift));
  });

  // ── Scissor kicks ─────────────────────────────────────────────────────────
  reg(['scissor kicks', 'flutter kicks', 'heel taps',
       'prone leg raise', 'prone leg raise (left)', 'prone leg raise (right)'], () => {
    const p = phase(0.9);
    const cx = 100;
    // lying on back, legs alternating
    const lLegY = osc(148, 128, p);
    const rLegY = osc(128, 148, p);
    // torso horizontal
    _svg.appendChild(el('circle', { cx: cx - 56, cy: 148, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx - 44, 148, cx + 20, 148));
    // arms by sides
    _svg.appendChild(line(cx - 30, 148, cx - 32, 162));
    _svg.appendChild(line(cx + 5, 148, cx + 7, 162));
    // legs
    _svg.appendChild(line(cx + 20, 148, cx + 36, lLegY));
    _svg.appendChild(line(cx + 36, lLegY, cx + 52, lLegY + 4));
    _svg.appendChild(line(cx + 20, 148, cx + 32, rLegY));
    _svg.appendChild(line(cx + 32, rLegY, cx + 48, rLegY + 4));
  });

  // ── Glute bridge / single leg bridge / slick floor bridges ───────────────
  reg(['glute bridges', 'glute bridges (hold)', 'glute bridges with abduction',
       'slick floor bridges curls', 'single leg glute bridge (left)',
       'single leg glute bridge (right)'], () => {
    const p = phase(0.4);
    const cx = 100;
    const hipY = osc(155, 130, p);
    // lying on back, hips up
    _svg.appendChild(el('circle', { cx: cx - 56, cy: 158, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx - 44, 158, cx - 14, hipY));   // upper back → hips
    _svg.appendChild(line(cx - 14, hipY, cx + 16, 165));   // thigh
    _svg.appendChild(line(cx + 16, 165, cx + 18, 185));    // shin
    // other leg
    _svg.appendChild(line(cx - 14, hipY, cx + 8, 165));
    _svg.appendChild(line(cx + 8, 165, cx + 10, 185));
    // arms by sides
    _svg.appendChild(line(cx - 36, 158, cx - 38, 172));
    _svg.appendChild(line(cx - 10, 158, cx - 8, 172));
  });

  // ── Donkey kicks ──────────────────────────────────────────────────────────
  reg(['donkey kicks (right)', 'donkey kicks (left)'], () => {
    const p = phase(0.5);
    const cx = 100;
    const kickY = osc(140, 110, p);
    // on all fours
    _svg.appendChild(el('circle', { cx: cx - 36, cy: 128, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx - 24, 132, cx + 16, 140));  // body
    // front arms
    _svg.appendChild(line(cx - 16, 134, cx - 20, 158));
    _svg.appendChild(line(cx + 0,  136, cx + 4,  158));
    // grounded leg
    _svg.appendChild(line(cx + 16, 140, cx + 22, 160));
    _svg.appendChild(line(cx + 22, 160, cx + 20, 178));
    // kick leg
    _svg.appendChild(line(cx + 16, 140, cx + 28, kickY));
    _svg.appendChild(line(cx + 28, kickY, cx + 38, kickY - 4));
  });

  // ── Fire hydrant ──────────────────────────────────────────────────────────
  reg(['fire hydrant (right)', 'fire hydrant (left)'], () => {
    const p = phase(0.5);
    const cx = 100;
    const legAngle = osc(0, 30, p);  // degrees out to side
    const hydrantX = osc(cx + 16, cx + 40, p);
    const hydrantY = osc(140, 128, p);
    // on all fours
    _svg.appendChild(el('circle', { cx: cx - 36, cy: 128, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx - 24, 132, cx + 16, 140));
    _svg.appendChild(line(cx - 16, 134, cx - 20, 158));
    _svg.appendChild(line(cx + 0,  136, cx + 4,  158));
    _svg.appendChild(line(cx + 16, 140, cx + 22, 162));
    _svg.appendChild(line(cx + 22, 162, cx + 20, 178));
    // hydrant leg
    _svg.appendChild(line(cx + 16, 140, hydrantX, hydrantY));
    _svg.appendChild(line(hydrantX, hydrantY, hydrantX + 8, hydrantY + 16));
  });

  // ── Clamshell ─────────────────────────────────────────────────────────────
  reg(['clamshell (right)', 'clamshell (left)'], () => {
    const p = phase(0.4);
    const cx = 100;
    const openY = osc(148, 128, p);
    // lying on side
    _svg.appendChild(el('circle', { cx: cx - 56, cy: 140, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx - 44, 144, cx + 10, 150));  // body
    // bottom leg straight
    _svg.appendChild(line(cx + 10, 150, cx + 26, 162));
    _svg.appendChild(line(cx + 26, 162, cx + 38, 174));
    // top leg lifts (clamshell)
    _svg.appendChild(line(cx + 10, 150, cx + 24, openY));
    _svg.appendChild(line(cx + 24, openY, cx + 38, openY + 12));
    // arm support
    _svg.appendChild(line(cx - 36, 144, cx - 38, 158));
  });

  // ── Plank / commando plank / spider plank ────────────────────────────────
  reg(['commando plank', 'spider + cross plank', 'high plank walk out',
       'high plank walk out (ikke opp)', 'plank jack shoulder taps',
       'plank with alternating arm raise', 'reverse foream plank',
       'walkouts to forearm plank'], () => {
    const p = phase(0.5);
    const cx = 100;
    const armSwing = osc(0, 12, p);
    // forearm plank
    _svg.appendChild(el('circle', { cx: cx - 52, cy: 130, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx - 40, 133, cx + 42, 133));
    _svg.appendChild(line(cx - 20, 133, cx - 30, 152));
    _svg.appendChild(line(cx - 30, 152, cx - 16, 158));  // forearm
    _svg.appendChild(line(cx + 6, 133, cx - 4 + armSwing, 152));
    _svg.appendChild(line(cx - 4 + armSwing, 152, cx + 10, 158));
    _svg.appendChild(line(cx + 42, 133, cx + 48, 152));
    _svg.appendChild(line(cx + 48, 152, cx + 52, 162));
    _svg.appendChild(line(cx + 42, 133, cx + 44, 152));
    _svg.appendChild(line(cx + 44, 152, cx + 46, 162));
  });

  // ── Flutter kicks / V-sit bicycles ────────────────────────────────────────
  reg(['v sit bicycles', 'seated knee tucks', 'kayak abs', 'l-crunch (left)', 'l-crunch (right)'], () => {
    const p = phase(0.7);
    const cx = 100;
    const hipAngle = osc(50, 80, p);  // v-sit angle
    const legY  = osc(130, 110, p);
    // V-sit
    _svg.appendChild(el('circle', { cx, cy: 125, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx, 137, cx, 160));  // torso leaning back
    // legs up
    _svg.appendChild(line(cx, 160, cx + 24, legY));
    _svg.appendChild(line(cx + 24, legY, cx + 36, legY + 8));
    _svg.appendChild(line(cx, 160, cx - 18, 150));
    _svg.appendChild(line(cx - 18, 150, cx - 28, 160));
    // arms forward
    _svg.appendChild(line(cx - 10, 145, cx - 22, 134));
    _svg.appendChild(line(cx + 10, 145, cx + 22, 134));
  });

  // ── Walkouts / squat to walkout ───────────────────────────────────────────
  reg(['walkouts', 'squat to walkout', 'roll down',
       'plank to downward dog', 'downward dog toe touch'], () => {
    const p = phase(0.4);
    const cx = 100;
    if (p < 0.5) {
      // bending forward, hands reaching ground
      const pp = p / 0.5;
      const hipAngle = osc(100, 140, pp);
      const handY    = osc(90, 165, pp);
      const headY    = osc(38, 80, pp);
      standing({
        cx, headY,
        neckY: headY + 18,
        hipY: osc(88, 120, pp),
        lHa: { x: cx - osc(20, 40, pp), y: handY },
        rHa: { x: cx + osc(20, 40, pp), y: handY },
        lEl: { x: cx - osc(22, 30, pp), y: osc(85, 130, pp) },
        rEl: { x: cx + osc(22, 30, pp), y: osc(85, 130, pp) },
      });
    } else {
      // walking hands out to plank
      const pp = (p - 0.5) / 0.5;
      _svg.appendChild(el('circle', { cx: cx - 52, cy: 130, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
      _svg.appendChild(line(cx - 40, 133, cx + 42, 133));
      _svg.appendChild(line(cx - 18, 133, cx - 22, 158));
      _svg.appendChild(line(cx - 22, 158, cx - 20, 165));
      _svg.appendChild(line(cx + 8, 133, cx + 12, 158));
      _svg.appendChild(line(cx + 12, 158, cx + 10, 165));
      _svg.appendChild(line(cx + 42, 133, cx + 50, 155));
      _svg.appendChild(line(cx + 50, 155, cx + 52, 165));
    }
  });

  // ── Side bends ────────────────────────────────────────────────────────────
  reg(['side bends', 'dynamic side bends'], () => {
    const p = phase(0.5);
    const cx = 100;
    const lean = osc(-16, 16, p);
    standing({
      cx, headY: 38,
      lSh: { x: cx - 18 + lean, y: 64 },
      rSh: { x: cx + 18 + lean, y: 64 },
      lEl: { x: cx - 10 + lean * 2, y: 82 },
      rEl: { x: cx + 30 + lean * 2, y: 72 },
      lHa: { x: cx - 6 + lean * 3, y: 100 },
      rHa: { x: cx + 40 + lean * 3, y: 90 },
    });
  });

  // ── Hip rotations / hip openers ───────────────────────────────────────────
  reg(['hip rotations (left)', 'hip rotations (right)',
       'hip openers', 'hip openers (left)', 'hip openers (right)',
       'standig hip rotations', 'standing hip rotations',
       'standing hip rotations (left)', 'standing hip rotations (right)',
       'standing hip rotation', '90/90 flip hip mobility'], () => {
    const p = phase(0.5);
    const cx = 100;
    const kneeSwing = osc(-20, 20, p);
    standing({
      cx, headY: 38,
      lKn: { x: cx - 14 + kneeSwing, y: 143 },
      rKn: { x: cx + 14 - kneeSwing, y: 143 },
    });
  });

  // ── Stretch poses (seated/lying) ──────────────────────────────────────────
  reg(['seated hamstring strech', 'knees to chest strech',
       'seated lower back strech (left)', 'seated lower back strech (right)',
       'figure 4 strech  (left)', 'figure 4 strech  (right)',
       'figure 4 strech (left)', 'figure 4 strech (right)',
       'figure 4 strech (left) rumpe', 'figure 4 strech (right) rumpe',
       'crossed-legged chest to floor', 'pigeon pose (left) - toye rumpe',
       'pigeon pose (right) - toye rumpe', 'pigeon pose (left) - tøye rumpe',
       'pigeon pose (right) - tøye rumpe', 'childs pose',
       'active calf & hamstring strech', 'pendulum hamstring strech',
       'standing quad strech (left)', 'standing quad strech (right)',
       '4 way strech (left)', '4 way strech (right)',
       'spinal twist (left)', 'spinal twist (right)'], () => {
    const p = phase(0.15);
    const cx = 100;
    const fwd = osc(0, 22, p);  // gentle forward lean
    // seated forward fold
    _svg.appendChild(el('circle', { cx: cx - 40, cy: 130 - fwd, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx - 28, 134 - fwd, cx - 28 + fwd * 0.8, 150));  // torso
    _svg.appendChild(line(cx - 28, 134 - fwd, cx - 16, 148));    // arm reach
    _svg.appendChild(line(cx - 16, 148, cx + 10, 158));
    _svg.appendChild(line(cx - 28 + fwd * 0.8, 150, cx - 10, 162));  // thigh
    _svg.appendChild(line(cx - 10, 162, cx + 16, 162));              // shin
  });

  // ── Cat-cow / cobra / childs pose ────────────────────────────────────────
  reg(['cat to cow strech', 'cobra'], () => {
    const p = phase(0.3);
    const cx = 100;
    const arch = osc(0, 18, p);
    // on all fours, spine arching
    _svg.appendChild(el('circle', { cx: cx - 36, cy: 132 - arch / 2, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    // spine curve
    _svg.appendChild(el('path', {
      d: `M ${cx - 24} ${136 - arch / 2} Q ${cx} ${140 - arch} ${cx + 16} ${138}`,
      stroke: '#222', 'stroke-width': 3, fill: 'none', 'stroke-linecap': 'round'
    }));
    _svg.appendChild(line(cx - 22, 138 - arch / 2, cx - 24, 160));
    _svg.appendChild(line(cx + 2, 138, cx + 4, 160));
    _svg.appendChild(line(cx + 16, 138, cx + 22, 160));
    _svg.appendChild(line(cx + 22, 160, cx + 20, 175));
    _svg.appendChild(line(cx + 16, 138, cx + 18, 160));
    _svg.appendChild(line(cx + 18, 160, cx + 16, 175));
  });

  // ── Shoulder stretch / elbow rotations / wrist warmup ────────────────────
  reg(['cross-body shoulder strech', 'chest openers with rotation',
       'elbow rotations', 'wrist warm-up', 'rotation toe touches',
       'side to side rotations'], () => {
    const p = phase(0.6);
    const cx = 100;
    const armOut = osc(-30, 30, p);
    standing({
      cx, headY: 38,
      lSh: { x: cx - 18, y: 64 },
      rSh: { x: cx + 18, y: 64 },
      lEl: { x: cx - 30 + armOut, y: 82 },
      rEl: { x: cx + 30 - armOut, y: 82 },
      lHa: { x: cx - 36 + armOut * 1.4, y: 68 },
      rHa: { x: cx + 36 - armOut * 1.4, y: 68 },
    });
  });

  // ── Open book / overhead lat stretch / lying rotations ────────────────────
  reg(['open book (left)', 'open book (right)',
       'overhead lat strech ', 'overhead lat strech (left)', 'overhead lat strech (right)',
       'lying leg extensions to the right', 'lying leg extensions to the eft'], () => {
    const p = phase(0.3);
    const cx = 100;
    const armAngle = osc(0, 28, p);
    standing({
      cx, headY: 38,
      lSh: { x: cx - 18, y: 64 },
      rSh: { x: cx + 18, y: 64 },
      lEl: { x: cx - 20 - armAngle, y: 58 },
      rEl: { x: cx + 20 + armAngle, y: 58 },
      lHa: { x: cx - 18 - armAngle * 1.6, y: 46 },
      rHa: { x: cx + 18 + armAngle * 1.6, y: 46 },
    });
  });

  // ── Robot arms / heel taps (standing) ─────────────────────────────────────
  reg(['robot arms'], () => {
    const p = phase(0.6);
    const cx = 100;
    const lArmAngle = osc(0, 40, p);
    const rArmAngle = osc(40, 0, p);
    standing({
      cx, headY: 38,
      lEl: { x: cx - 36, y: 78 },
      rEl: { x: cx + 36, y: 78 },
      lHa: { x: cx - 28 + lArmAngle, y: 66 },
      rHa: { x: cx + 28 - rArmAngle, y: 66 },
    });
  });

  // ── Wood chops ────────────────────────────────────────────────────────────
  reg(['wood chops (left)', 'wood chops (right)'], () => {
    const p = phase(0.5);
    const cx = 100;
    const chop = osc(0, 1, p);
    standing({
      cx, headY: 38,
      lSh: { x: cx - 18 + chop * 20, y: 64 },
      rSh: { x: cx + 18 + chop * 20, y: 64 },
      lEl: { x: cx - 10 + chop * 30, y: osc(52, 88, chop) },
      rEl: { x: cx + 10 + chop * 30, y: osc(52, 88, chop) },
      lHa: { x: cx + chop * 40, y: osc(44, 100, chop) },
      rHa: { x: cx + 20 + chop * 40, y: osc(44, 100, chop) },
    });
  });

  // ── Plank to downward dog ────────────────────────────────────────────────
  reg(['plank to downward dog'], () => {
    const p = phase(0.3);
    const cx = 100;
    const hipLift = osc(133, 105, p);
    _svg.appendChild(el('circle', { cx: cx - 52, cy: hipLift - 12, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    // hands on floor
    _svg.appendChild(line(cx - 40, hipLift - 8, cx - 30, 162));
    _svg.appendChild(line(cx - 30, 162, cx - 16, 165));
    // hip / torso
    _svg.appendChild(line(cx - 40, hipLift - 8, cx + 10, hipLift));
    // legs
    _svg.appendChild(line(cx + 10, hipLift, cx + 22, 160));
    _svg.appendChild(line(cx + 22, 160, cx + 20, 178));
    _svg.appendChild(line(cx + 10, hipLift, cx + 16, 160));
    _svg.appendChild(line(cx + 16, 160, cx + 14, 178));
  });

  // ── Hip flexor stretch (standing lunge-based) ─────────────────────────────
  reg(['hip flexor strech', 'side to side lunge'], () => {
    const p = phase(0.3);
    const cx = 100;
    const lunge = osc(0, 22, p);
    standing({
      cx, headY: 38,
      lKn: { x: cx - 32, y: 148 + lunge },
      lFo: { x: cx - 40, y: 188 },
      rKn: { x: cx + 24, y: 148 - lunge },
      rFo: { x: cx + 22, y: 188 },
    });
  });

  // ── Heckleløper / high knees ──────────────────────────────────────────────
  reg(['hekkeløper (venstre)', 'hekkeløper (høyre)', 'hekkeloper (venstre)', 'hekkeloper (hoyre)'], () => {
    const p = phase(0.8);
    const cx = 100;
    const kneeUp = osc(145, 110, p);
    standing({
      cx, headY: 36,
      lKn: { x: cx - 14, y: kneeUp },
      lFo: { x: cx - 10, y: kneeUp + 28 },
      rKn: { x: cx + 16, y: 148 },
      rFo: { x: cx + 18, y: 185 },
    });
  });

  // ── Seated knee tucks / reverse plank ────────────────────────────────────
  reg(['reverse plank triceps dips'], () => {
    const p = phase(0.4);
    const cx = 100;
    const dip = osc(0, 16, p);
    // reverse plank facing up
    _svg.appendChild(el('circle', { cx: cx + 50, cy: 130 + dip, r: 12, fill: 'none', stroke: '#222', 'stroke-width': 2.5 }));
    _svg.appendChild(line(cx + 38, 134 + dip, cx - 30, 134));
    _svg.appendChild(line(cx + 20, 134 + dip / 2, cx + 24, 158));
    _svg.appendChild(line(cx + 24, 158, cx + 22, 165));
    _svg.appendChild(line(cx + 5, 134, cx + 8, 158));
    _svg.appendChild(line(cx + 8, 158, cx + 6, 165));
    _svg.appendChild(line(cx - 30, 134, cx - 34, 152));
    _svg.appendChild(line(cx - 34, 152, cx - 36, 162));
    _svg.appendChild(line(cx - 30, 134, cx - 28, 152));
    _svg.appendChild(line(cx - 28, 152, cx - 26, 162));
  });

  // ── Default: generic "move" animation ────────────────────────────────────
  function defaultAnim() {
    const p = phase(0.5);
    const cx = 100;
    standing({
      cx, headY: 38,
      lEl: { x: cx - 28, y: osc(78, 65, p) },
      rEl: { x: cx + 28, y: osc(65, 78, p) },
      lHa: { x: cx - 26, y: osc(96, 82, p) },
      rHa: { x: cx + 26, y: osc(82, 96, p) },
      lKn: { x: cx - 16, y: osc(143, 138, p) },
      rKn: { x: cx + 16, y: osc(138, 143, p) },
    });
  }

  // ── Public API ─────────────────────────────────────────────────────────────
  function stop() {
    if (_raf) { cancelAnimationFrame(_raf); _raf = null; }
    if (_svg) clear();
  }

  function show(exerciseName) {
    _svg = document.getElementById('exercise-anim');
    if (!_svg) return;

    stop();
    _t = 0;

    const key = (exerciseName || '').toLowerCase().trim();
    const fn  = animations[key] || defaultAnim;

    const FPS = 30;
    let last = null;

    function loop(ts) {
      if (last !== null) _t += (ts - last) / 1000;
      last = ts;
      clear();
      fn();
      _raf = requestAnimationFrame(loop);
    }
    _raf = requestAnimationFrame(loop);
  }

  return { show, stop };

})();
