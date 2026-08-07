import io, re, sys

P = r"C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\9a0ff112-f2f7-4e19-b425-76397340666b\scratchpad\board.html"
s = io.open(P, encoding="utf-8").read()
orig = s
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70])
    s = s.replace(old, new)

# ---- 1. title -------------------------------------------------------------
rep("<title>3J Leg-3 v2 — finalisation board</title>",
    "<title>3J Leg-3 — v2 closed, v3 open</title>")

# ---- 2. header ------------------------------------------------------------
i = s.index("<header>"); j = s.index("</header>") + len("</header>")
header = """<header>
  <div class="eyebrow">3J Leg-3 &middot; four-split occupancy to BEM</div>
  <h1>v2 closed &middot; v3 open</h1>
  <p class="sub">Two generations on one board. <b>v2 is finished &mdash; all 49 tasks</b>
     (<span class="mono">improvements/v2/3rdJ_L3_v2_implementation.md</span>). <b>v3 is the plan for what v2 left
     on your desk</b> (<span class="mono">improvements/v3/3rdJ_L3_v3_implementation.md</span>): the three decisions
     that were carried here as a bullet list, plus the three pieces of work that make them decidable. <b>A bullet
     list is not a task</b> &mdash; it has no test, no artefact, and nothing that fails if it is ignored, which is
     how a fourth item quietly fell off this list last week without anyone deciding to drop it.<br><br>
     🔴 <b>Before writing the plan I read the code behind all three decisions instead of my own summary of them,
     and all three descriptions on this board were incomplete &mdash; one of them plainly wrong.</b> The corrections
     are in the three cards below. <b>None of them clears a failure and none of them moves a band.</b></p>
  <div class="stamp mono">State as of <b>2026-08-06</b> &middot; <b>49 v2 tasks done</b> &middot; <b>6 v3 tasks: 3 your call, 3 ready</b>
     &middot; v3 plan opened today, nothing executed &middot; no cluster contact, zero simulation cells
     &middot; evidence for the three corrections is reproducible from the repo &mdash; commands in the plan&rsquo;s appendix</div>
</header>"""
s = s[:i] + header + s[j:]

# ---- 3. decisions section -------------------------------------------------
# The old block is KEPT verbatim below the new one. Most of its items are closed
# work rather than open decisions, and they are the version the user last read;
# deleting them to make room for a tidier list would lose prose that exists
# nowhere else in this file.
i = s.index('<section class="decisions">'); j = s.index("</section>", i) + len("</section>")
old_block = s[i:j]
k = old_block.index("<ol>")
old_ol = old_block[k:]                      # the original list, untouched
assert old_ol.rstrip().endswith("</section>")   # the slice carried the closer with it
old_ol = old_ol.rstrip()[: -len("</section>")].rstrip()
dec = """<section class="decisions">
  <h2>Three things are waiting on you &mdash; and each description here was wrong or incomplete until today</h2>
  <p class="why" style="margin:0 0 4px">They are the same three that closed the v2 board. What changed is that
     they now have <b>evidence behind them</b> instead of a one-line summary. I read the scoring code, the training
     logs and the shipped result tables. <b>Every number below is reproducible with a command in the plan&rsquo;s
     appendix</b>, and each correction runs <em>against</em> the convenient answer rather than towards it.<br><br>
     🔴 <b>An empty board is not proof the work is finished.</b> Yesterday this board said nothing was left. It lasted
     forty minutes. The three below will not surface by themselves &mdash; that is why they are now tasks with test
     methods rather than bullets.</p>
  <ol>
    <li><strong>The hotel rule &mdash; decidable today, and it carries the trap. <span class="mono">V3-H3</span></strong>
      <span class="why">The hotel check requires <em>every</em> building to be in range; the shop check requires only the
      <em>middle</em> one. The scoring code discloses that under the shop rule the hotel check would <b>pass</b>.<br><br>
      🔴 <b>What this board did not say: the shop check fails under BOTH rules</b> &mdash; its middle building sits at
      <b>75.6</b> against a floor of <b>80</b> &mdash; and so does the office check. <b>So switching every channel to the
      middle-building rule would change exactly one status in the entire scorecard: the hotel failure becomes a pass.</b>
      A &ldquo;uniform principled rule&rdquo; whose only effect is to clear the one check under discussion is the same move
      that was reversed on 5 August, wearing better paperwork.<br><br>
      ⚖️ <b>And the principle already on file argues the other way.</b> The recorded reason for giving shops the middle-building
      rule was that <em>an all-buildings rule on a spread smaller than its own uncertainty reports noise as a verdict</em>.
      Measured: the office buildings span <b>28 %</b> of their band, shops <b>44 %</b> &mdash; and <b>hotels span 96 %</b>.
      Hotel buildings genuinely differ; that is signal, not noise. Applying the stated principle honestly gives the
      middle-building rule to offices and shops, keeps all-buildings for hotels, and <b>changes no status at all</b> &mdash;
      which is the one property gate-shopping cannot produce.<br><br>
      <b>Disclosure:</b> I measured those spreads <em>after</em> knowing which rule clears the hotel, so any boundary I
      proposed would not be blind. I am not proposing one. The statistic and the principle are the deliverable; the
      boundary is yours.</span></li>
    <li><strong>Which model the pipeline should ship &mdash; and the re-run is not what I told you it was. <span class="mono">V3-H1</span></strong>
      <span class="why">The method document says: keep the models that pass every check, then take the best retail score,
      and <em>never</em> select on a single blended number. The code selects on a single blended number, one containing
      neither retail measure. That much is unchanged.<br><br>
      🔴 <b>Three things I had wrong.</b> First, I described the code fix as a re-run implying five retrainings. It is not:
      the documented rule&rsquo;s winner is <b>seed 0 at its final epoch</b>, and the final epoch&rsquo;s weights are saved
      every run &mdash; so the model already exists. The real cost is the downstream cascade, which reopens the frozen
      deliverable.<br><br>
      Second, <b>the documented rule was never implementable as written.</b> Its first clause requires passing every hard
      check &mdash; but two of those checks can only be computed <em>after</em> generating a full 418 MB diary pool. There is
      no per-epoch pool and never was, so evaluating the document&rsquo;s own rule would have cost <b>75 generation
      cascades</b>. The &ldquo;separate selection step&rdquo; the code&rsquo;s docstring defers to was not merely unwritten;
      it was unaffordable.<br><br>
      Third, and this is what should decide it: <b>both rules select on teacher-forced numbers that the audit already
      showed are blind to person-level retail skill.</b> Switching rules buys <b>+0.022</b> of a measure that does not
      measure the thing, at the price of a full re-cascade &mdash; while the five seeds are separated by a sixth of their
      own spread. <b>I am not arguing from cost.</b> I am recording that the expensive option optimises a number the
      pipeline&rsquo;s own audit disqualified.</span></li>
    <li><strong>The exclusivity check &mdash; and this board called it the wrong thing. <span class="mono">V3-H2</span></strong>
      <span class="why">🔴 This card previously read <em>&ldquo;whether one <b>office</b> check should fail rather than
      warn&rdquo;</em>. <b>It is not an office check.</b> It is the Step-4 check that counts time slots where a person is
      recorded in two places at once.<br><br>
      <b>And the choice as posed has no consequence whatsoever.</b> Three lines of arithmetic in the validator: a slot with
      two channels active <em>is</em> a pairwise conflict, and vice versa. So this check can be non-zero <b>only when the
      hard exclusivity check is already failing</b> &mdash; and that one fails at anything above zero. Its warning band sits
      entirely inside territory where a hard failure has already fired. <b>Raising it to failure catches nothing it does not
      already catch; it just reports one event as two failures.</b><br><br>
      <b>The real gap is elsewhere, and it was dropped.</b> The task that would close it &mdash; a check that compares each
      respondent&rsquo;s generated shopping against their own observed shopping &mdash; was written down as a deliverable
      on 5 August and <b>never made it onto any list</b>. It is the thing this check was mistakenly credited with being.
      It is now <span class="mono">V3-J1</span>, and it is the only v3 task with a real chance of producing a new failure.</span></li>
  </ol>

  <h2 style="margin-top:26px">Where you last read them &mdash; the v2 list, kept verbatim</h2>
  <p class="why" style="margin:0 0 4px">Everything below is the block this section held when the v2 board closed.
     <b>Most of it is closed work rather than open decisions</b> &mdash; it accumulated under a &ldquo;waiting on you&rdquo;
     heading, which is part of why the three genuine decisions were easy to lose. It is kept rather than tidied away:
     it is the version you read, and the three items above supersede only the parts they name.</p>
  """ + old_ol + """
</section>"""
s = s[:i] + dec + s[j:]

# ---- 4. new work packages at the top of WP --------------------------------
anchor = 'const WP=[\n ["A","The submitted 2J paper first",['
assert s.count(anchor) == 1
newwp = '''const WP=[
 ["H","v3 &middot; the three open decisions — your call",[
  ["V3-H1","The val_score selection rule: fix the document, or fix the code","waiting","Cost re-derived: NOT five retrainings — the documented rule's winner is seed 0's final epoch and those weights are saved every run. But the documented rule was never implementable as written, and BOTH rules select on a number the audit showed is blind to person-level retail skill","decision · evidence complete",
   "<b>The defect is unchanged and it is real.</b> The method document mandates: keep every model that passes the hard checks, then take the best retail score, and <em>never</em> select on a single blended number — citing it as a lesson already learned once. The code selects on a blended number that contains <b>neither</b> retail measure. The two rules pick different epochs in <b>four of the five seeds</b>, worth <b>5.6 %</b> of retail accuracy, and the shipped seed is exactly the winner of the forbidden number and fourth of five on the one the document names.<br><br>🔴 <b>What I had wrong, first.</b> I described fixing the code as a re-run without saying what kind. The documented rule&rsquo;s winner across all 75 epochs is <b>seed 0, epoch 15</b> — the <em>final</em> epoch — and the training code writes the final epoch&rsquo;s weights to disk every single epoch. <b>The model the document would have chosen already exists.</b> The cost is one generation pass plus the full downstream cascade, and that cascade reopens the frozen deliverable. That is still expensive, but it is a different decision from the one I described.<br><br>🔴 <b>Second, and worse: the documented rule could never have been run.</b> Its first clause is <em>&ldquo;passing every hard check&rdquo;</em>. Two of those checks — midday error and transitions per day — are computed from the generated diary pool, not from training. There is no per-epoch pool. Evaluating the document&rsquo;s own rule would have required <b>75 full generation cascades</b>. The docstring&rsquo;s promise of a &ldquo;separate selection step later&rdquo; was not just unwritten, it was unaffordable — and on this data the clause is inert anyway: every one of the 75 epochs clears every check that <em>is</em> measurable, by wide margins.<br><br>🔴 <b>Third, the one that should actually decide it.</b> Both rules read the same two teacher-forced columns of the training log. <b>Those are the columns the audit already proved blind:</b> all ten retail checks report identical results on a pool where shopping was randomly swapped between people, and the two headline ones pass a pool with shopping deleted entirely. So the expensive option buys <b>+0.022</b> on a number that does not measure whether the model got individuals right, while the five seeds sit within a sixth of a standard deviation of each other. <b>The argument against the re-run is not that it costs too much. It is that it optimises the wrong number.</b><br><br><b>Three options, and the third is the only one that does not commit before the evidence exists:</b> fix the document and carry the gap as a limitation; fix the code and re-cascade; or fix the document <em>now</em> with a written trigger that reopens the question if <span class='mono'>V3-J1</span>&rsquo;s person-level check ranks the seeds differently."],
  ["V3-H2","The exclusivity check: fail, or warn","waiting","The choice as posed has NO detection consequence — this check is arithmetically incapable of firing while the hard check passes. Also: it is not an office check, which is what this board called it","decision · reframed",
   "<b>The premise it was carried under is false.</b> The note read: <em>&ldquo;it is currently the only retail-touching person-level discriminator and it cannot fail.&rdquo;</em> Three lines of the validator settle it. The hard check counts slots where more than one channel is active; this check counts the same slots, split by which pair. <b>One is zero if and only if the other is</b> — and the hard one fails at anything above zero. <b>So this check can only ever be non-zero when a hard failure has already fired.</b> Its entire warning band lies inside already-failing territory.<br><br>On the shipped pool both read exactly zero: <b>0 of 6,149,856 slots</b>. In the audit&rsquo;s shuffle test both fired together — the same event, reported twice, at two severities. <b>Raising this to a failure changes no outcome; it double-counts one event on the scorecard.</b><br><br><b>The recommendation is to leave it as a warning, say in the documentation why</b> (it is a decomposition of the hard check — it tells you <em>which pair</em> conflicted) <b>and build the check that was actually meant</b>: <span class='mono'>V3-J1</span>.<br><br><b>The claim above is an impossibility claim, so it gets attacked rather than asserted.</b> The test method is to introduce exactly <em>k</em> conflicts into the pool and confirm no perturbation exists that makes this check fire while the hard one passes."],
  ["V3-H3","The all-buildings vs middle-building rule, for all three channels at once","waiting","Retail fails under BOTH rules — so a uniform middle-building rule would change exactly ONE status in the whole scorecard, and it is the hotel failure. The principle already on file argues for keeping all-buildings for hotels, and changes nothing","decision · decidable today",
   "<b>The full picture, from the shipped result table, 56 buildings per channel, no simulation:</b><br><br><span class='mono'>office &nbsp;61.7 / <b>71.0</b> / 90.2 &nbsp;band [100, 200] &nbsp;→ fails under both rules</span><br><span class='mono'>retail &nbsp;63.6 / <b>75.6</b> / 96.8 &nbsp;band [80, 155] &nbsp;→ fails under both rules</span><br><span class='mono'>hotel &nbsp;203.3 / <b>260.5</b> / 318.4 &nbsp;band [180, 300] &nbsp;→ FAILS all-buildings, PASSES middle-building</span><br><br>🔴 <b>The shop check fails under the middle-building rule too</b> — its middle building is <b>5.5 % below the floor</b>. This board&rsquo;s framing implied the rules were a live question for two channels. They are not. <b>Exactly one gate in the entire scorecard turns on this choice, and it is the hotel failure under discussion.</b><br><br>⚖️ <b>The principle that is already written into the code argues against the tempting answer.</b> Shops were given the middle-building rule because <em>&ldquo;an all-buildings rule on a spread smaller than its own uncertainty reports noise as a verdict&rdquo;</em> — a statement about spread relative to the band. Measured: offices span <b>28 %</b> of their band, shops <b>44 %</b>, <b>hotels 96 %</b>. Hotel buildings are not clustered inside their uncertainty; they genuinely differ, and an all-buildings rule on them reports signal. <b>Any boundary drawn between shops and hotels gives: middle-building for offices and shops, all-buildings for hotels — and changes zero statuses</b>, because offices and shops fail either way.<br><br><b>Disclosure, because it is load-bearing:</b> I computed these spreads knowing which rule clears the hotel. A boundary I proposed now would not be blind, so <b>I am not proposing one</b>. The deliverable is the statistic and the principle. The reason to trust this particular construction is not my judgement — it is that <b>the resulting rule changes nothing</b>, which is exactly what a rule chosen to clear a gate cannot do.<br><br><b>No band value moves under any option.</b> The one option that does move a status (uniform middle-building) reopens the frozen deliverable&rsquo;s headline scorecard and would be a re-publication, not an edit."]]],
 ["J","v3 &middot; what makes those decidable (derived scope)",[
  ["V3-J1","Build the person-level retail check that was written down and then dropped","open","The audit's deliverable item 2, never built, never on any list. It is the check the exclusivity gate was mistakenly credited as being — and the only v3 task that could produce a new failure","ready · local, 418 MB pool on this machine",
   "<b>The gap, stated plainly.</b> Ten retail checks report <em>identical</em> results on a pool where shopping behaviour was randomly swapped between people within each year, day-type and province — every rate, every shape, every total preserved, only the link between a person and their own shopping destroyed. <b>The battery measures population averages, not whether the model got individuals right.</b> A check for that was written down as a deliverable on 5 August. It was never built and never appeared on the owed list.<br><br><b>Design.</b> Compare each respondent&rsquo;s generated shopping vector against their own observed one; grade it against the <em>shuffle null</em> — what random person-assignment scores on the same statistic — so the bar comes from the data rather than from an invented constant. Band written down before the observed value is computed.<br><br><b>Seen failing, four arms, and the control is the load-bearing one:</b> untouched pool must pass; within-cell shuffle must fail; deleted shopping must fail; a half-shuffle to show the check is graded rather than binary.<br><br>🔴 <b>A new failure is a live possibility and is not a reason to weaken the check.</b> If the shipped pool cannot beat its own shuffle null, that is precisely the finding the audit pointed at, and it gets reported at whatever severity the pre-registered band gives.<br><br><b>First thing to verify, before any design:</b> that a per-respondent <em>observed</em> shopping vector exists for the pool rows at all. If it does not exist for every row, scope the check to the rows where it does and say so — <b>do not substitute a population average and call it person-level</b>, which is the defect this task exists to fix."],
  ["V3-J2","Rescue the evidence that exists only in temporary folders","open","Part done today: the five-seed training logs — the entire evidence base for the model-selection decision — existed ONLY in a session scratchpad and are now in the repo. The audit's own falsifier is already GONE and must be rewritten","partly done today",
   "<b>The principle was applied to two files last night and not to the rest.</b> Two tests were moved into the repo on the grounds that <em>a test living in a temporary folder is a test nobody will run again</em>. That was correct and incomplete.<br><br><b>Done in the same response as the v3 plan:</b> the five seeds&rsquo; training logs — 15 files, 49 KB, the entire evidence base for the model-selection decision — were copied into the repo. Every number in that decision is now reproducible from a checked-in file, with the commands printed in the plan.<br><br>🔴 <b>Already lost:</b> the scripts that perturbed the pool and proved ten retail checks blind. Not in the repo, not in any surviving scratchpad. <b>That was the only demonstration of the audit&rsquo;s central finding</b>, and it is also the test method the new person-level check needs. It has to be rewritten — inside <span class='mono'>V3-J1</span>, in the repo this time."],
  ["V3-J3","A ledger check that fails when an owed item goes missing","open","The defect has happened twice: this board said 'nothing is waiting on you' while three decisions were open, and a fourth deliverable left the list with nobody deciding to drop it","ready · ~100 lines plus falsifier",
   "<b>Two real incidents, not hypotheticals.</b> On 5 August the status line read <em>&ldquo;nothing&rdquo;</em> while three decisions were owed. And the deliverable that became <span class='mono'>V3-J1</span> left the ledger between one day and the next without anyone deciding to drop it.<br><br><b>The check:</b> the plan, the handoff prompt and this board must name the <em>same set</em> of owed items, and every one of them must have a task section with a test method. <b>A missing section is a hard failure, never a skip</b> — a checker that skipped absent items would have passed on 5 August, which is the vacuous-check pattern this project already catalogues sixteen kinds of.<br><br><b>Seen failing at least four ways, on a fixture, with the real files never touched</b> — and one of the four is <b>the repository exactly as it stood on 5 August</b>, which is not a synthetic perturbation but a state this project was really in."]]],
 ["A","The submitted 2J paper first",['''
s = s.replace(anchor, newwp)

# ---- 5. id prefix + new state --------------------------------------------
rep('<div class="id">${id.replace("V2-","")}</div>',
    '<div class="id">${id.replace(/^V[23]-/,"")}</div>')

rep('const S={done:["s-done","done"],decided:["s-decided","decided"],partial:["s-partial","partial"],\n         open:["s-open","open"],blocked:["s-blocked","blocked"]};',
    'const S={done:["s-done","done"],decided:["s-decided","decided"],partial:["s-partial","partial"],\n         open:["s-open","open"],blocked:["s-blocked","blocked"],waiting:["s-waiting","waiting"]};')

rep('const order=["done","decided","partial","open","blocked"];',
    'const order=["waiting","done","decided","partial","open","blocked"];')
rep('const labels={done:"done",decided:"decided",partial:"in progress",open:"ready",blocked:"blocked"};',
    'const labels={done:"done",decided:"decided",partial:"in progress",open:"ready",blocked:"blocked",waiting:"your call"};')
rep('const filterOrder=["partial","open","blocked","decided","done"];',
    'const filterOrder=["waiting","open","partial","blocked","decided","done"];')
rep('const colv={done:"var(--done)",decided:"var(--blue)",partial:"var(--hold)",open:"var(--idle)",blocked:"var(--stop)"};',
    'const colv={done:"var(--done)",decided:"var(--blue)",partial:"var(--hold)",open:"var(--idle)",blocked:"var(--stop)",waiting:"var(--call)"};')

# a "not closed" count must not read decisions as closed work
rep('const open=rows.filter(r=>r[2]!=="done"&&r[2]!=="decided").length;',
    'const open=rows.filter(r=>r[2]!=="done"&&r[2]!=="decided").length;')

# ---- 6. empty-filter copy -------------------------------------------------
i = s.index("const EMPTY={"); j = s.index("};", i) + 2
empty = '''const EMPTY={
  partial:["Nothing is in progress.",
    "Three v3 tasks are <b>ready</b> and three are <b>your call</b>, so this is an ordinary empty bucket rather than "+
    "a finished project. One task is worked at a time and the next is promoted the moment it closes."],
  open:["No task is ready to start.",
    "Everything left is waiting on a decision. <b>An empty ready queue is not the same as a finished project</b> — "+
    "on 5 August this board looked complete, and one question about a failing check produced a task, a reverted "+
    "change and four findings."],
  blocked:["Nothing is blocked.","No v3 task needs the cluster, and none needs a simulation cell."],
  waiting:["Nothing is waiting on you.",
    "🔴 <b>This line was wrong once already.</b> It read &ldquo;nothing&rdquo; on 5 August while three decisions were open. "+
    "<span class='mono'>V3-J3</span> exists so a machine notices next time instead of a reader."],
  decided:["No task is in the <em>decided</em> state.",
    "A decision that has also been written into the code and the documents is filed as <b>done</b>, not "+
    "<b>decided</b> — so this bucket empties as decisions get implemented."],
  done:["Nothing is closed yet.",""],
  all:["No tasks.",""]
};'''
s = s[:i] + empty + s[j:]

# ---- 7. footer ------------------------------------------------------------
i = s.index("<footer>"); j = s.index("</footer>") + len("</footer>")
foot = """<footer>
  <div>Two plans, one board. <b>v2</b> — <span class="mono">improvements/v2/3rdJ_L3_v2_implementation.md</span>, 5,751 lines,
       49 of 49 closed. <b>v3</b> — <span class="mono">improvements/v3/3rdJ_L3_v3_implementation.md</span>, opened
       2026-08-06, 6 tasks, nothing executed yet.</div>
  <div class="mono">v3 evidence: improvements/v3/e4_seed_logs/ (rescued from a temp folder today) &middot;
       Step9_docs/outputs_step9_deliverable/step9_eui_by_channel.csv &middot; every figure has a reproduction command in the plan's appendix</div>
</footer>"""
s = s[:i] + foot + s[j:]

# ---- 8. a pill for the new state ------------------------------------------
# The five existing states use every hue in the palette, and none of them is
# right: "your call" is not a failure (red), not idle (grey), not settled
# (blue). So the palette gains one token pair, in the same soft/solid idiom,
# defined in all four theme blocks rather than only in the dark one.
tok_light = "--call:#6b4bb0; --call-soft:#efeaf8;"
tok_dark  = "--call:#b49af0; --call-soft:#231c33;"
# Line-based: the four theme blocks are exactly the four lines declaring --idle,
# and the light/dark pair is told apart by its own value rather than by position.
lines = s.split("\n")
hits = [n for n, ln in enumerate(lines) if "--idle:" in ln]
assert len(hits) == 4, hits
for n in hits:
    lines[n] = lines[n].rstrip() + " " + (tok_light if "#66707e" in lines[n] else tok_dark)
s = "\n".join(lines)

m = re.search(r"\.s-blocked\s*\{[^}]*\}", s)
assert m, "no .s-blocked rule found"
s = s[:m.end()] + "\n  .s-waiting{background:var(--call-soft); color:var(--call)}" + s[m.end():]

io.open(P, "w", encoding="utf-8").write(s)
print("bytes %d -> %d" % (len(orig), len(s)))
