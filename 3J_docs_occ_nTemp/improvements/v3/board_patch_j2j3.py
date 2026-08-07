import io
P = r"C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\9a0ff112-f2f7-4e19-b425-76397340666b\scratchpad\board.html"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90])
    s = s.replace(old, new)

# ---- V3-J2 row -----------------------------------------------------------
rep('["V3-J2","Rescue the evidence that exists only in temporary folders","open","Part done today: the five-seed training logs — the entire evidence base for the model-selection decision — existed ONLY in a session scratchpad and are now in the repo. The audit\'s own falsifier is already GONE and must be rewritten","partly done today",',
    '["V3-J2","Rescue the evidence that exists only in temporary folders","done","Five sets of evidence rescued — including this board\'s own source, which was being published from a temporary folder. The lost test was rebuilt, and it REPRODUCES the audit\'s finding while CORRECTING it: two checks credited with catching a scrambled person were catching something else entirely","closed today · 5 of 6 conditions, and the sixth is left failing on purpose",')

rep("<b>That was the only demonstration of the audit&rsquo;s central finding</b>, and it is also the test method the new person-level check needs. It has to be rewritten — inside <span class='mono'>V3-J1</span>, in the repo this time.\"],",
    "<b>That was the only demonstration of the audit&rsquo;s central finding</b>, and it is also the test method the new person-level check needs."
    "<br><br><hr><b>REBUILT — six versions of the data, six runs of the real checker.</b> The finding it was meant to preserve reproduces exactly: shuffle who did the shopping, and <b>all forty lines of the retail battery are byte-for-byte identical</b>. "
    "The battery measures populations, not people.<br><br>"
    "🔴 <b>And it corrects the original.</b> The audit reported that two checks <em>did</em> notice the shuffle. They did not. <b>Shuffling shopping alone puts two activities in the same half-hour</b> — someone recorded at home at 2pm inherits a stranger&rsquo;s 2pm shop — and those two checks fired on the <em>collision</em>, not on the scrambled person. "
    "The exclusivity check went from <b>0 %</b> to <b>1.42 %</b> of slots. The audit&rsquo;s own maxim, applied to the audit: <b>a change that breaks more than one thing cannot tell you which one it broke.</b><br><br>"
    "🔴 <b>So the day itself was moved instead — all thirteen channels at once, to a different person in the same year, province and day type.</b> Every row stays a coherent day, every population total is unchanged, and the only thing destroyed is <em>whose</em> day it is. "
    "<b>Out of 150 lines the checker prints, exactly FOUR move.</b> Two are the new person-level check; the other two are a single check on day-type ordering. "
    "<b>The entire Step-4 validation suite contains exactly two checks that can see the individual at all</b> — and one of them is a day old. That was written down as a prediction before the run.<br><br>"
    "<b>One condition is left failing, and the transcript says so.</b> I required the new check&rsquo;s number to fall by at least three times under the shuffle; it fell by 2.2 times. <b>The criterion is not being relaxed to fit</b> — it assumed the shipped data had person-level signal to lose, and the day before had already shown it has almost none. The run exits with an error code.<br><br>"
    "<b>Also rescued into the repo:</b> the five training logs, this board&rsquo;s own HTML, the additions-only run difference from last night, the output of the reverted change that the plan cites as its reference, and 26 sweep logs. <b>24 GB of regenerable simulation output was deliberately not kept.</b>\"],")

# ---- V3-J3 row -----------------------------------------------------------
rep('["V3-J3","A ledger check that fails when an owed item goes missing","open","The defect has happened twice: this board said \'nothing is waiting on you\' while three decisions were open, and a fourth deliverable left the list with nobody deciding to drop it","ready · ~100 lines plus falsifier",',
    '["V3-J3","A ledger check that fails when an owed item goes missing","done","BUILT AND SEEN FAILING SIX WAYS. The plan, the handoff and this board must now name the SAME open decisions, each with a real task section — and a machine checks it. One of the six perturbations exists only because a condition had never once been the one that fired","closed today · 7 of 7 arms",')

rep("<b>Seen failing at least four ways, on a fixture, with the real files never touched</b> — and one of the four is <b>the repository exactly as it stood on 5 August</b>, which is not a synthetic perturbation but a state this project was really in.\"]]],",
    "<b>Seen failing six ways, on copies, with the real files never touched:</b> an item deleted from the handoff; an item quietly downgraded on this board; the handoff replaced with the sentence &ldquo;nothing blocking&rdquo;; an item whose task section has been renamed away; the counter drifting from the table; and an item still marked open in the data but no longer <em>named</em> in the prose a reader sees.<br><br>"
    "<b>That last one exists because of a gap in my own first attempt.</b> After five perturbations, one of the four conditions had <b>never once been the one that fired</b> &mdash; so it had not been shown to work at all. The sixth exercises it, and it is the one that reproduces the 5 August failure most exactly: <b>the machine-readable field was never wrong; the sentence a human reads was.</b><br><br>"
    "🔴 <b>And a claim in this task&rsquo;s own description was wrong.</b> I wrote that one fixture would be <em>the repository exactly as it stood on 5 August</em>. It is not &mdash; those files are from the previous generation and this checker cannot read their vocabulary. What it actually reproduces is the 5 August <em>defect pattern</em> on today&rsquo;s files, using the wording the old handoff really used. <b>A weaker claim, and the true one.</b><br><br>"
    "<b>What it does not do, said plainly:</b> it checks that the three documents <em>agree</em>, not that they are <em>right</em>. If all three lose the same item on the same day, it passes.\"]]],")

# ---- header stamp --------------------------------------------------------
rep("&middot; <b>6 v3 tasks: 3 your call, 1 done, 2 ready</b>\n     &middot; <b>V3-J1 closed the same day it was written &mdash; and it failed</b>",
    "&middot; <b>6 v3 tasks: 3 done, 3 your call, 0 ready</b>\n     &middot; <b>all three tasks that were mine closed the day they were written &mdash; and the first one failed</b>")

rep("<b>A new failure is not "
    "a reason to weaken a check</b>, and the bar it failed was written before the first number existed.</p>",
    "<b>A new failure is not "
    "a reason to weaken a check</b>, and the bar it failed was written before the first number existed.<br><br>"
    "🔴 <b>All three of my tasks are now closed, and the third one measured the whole checker.</b> Move an entire generated day to a different person &mdash; same year, same province, same day type &mdash; and "
    "<b>only 4 of the 150 lines the Step-4 checker prints move at all.</b> Two of them are the check built yesterday. <b>Everything left on this board is a decision, and all three are yours.</b></p>")

io.open(P, "w", encoding="utf-8").write(s)
print("patched j2/j3")
