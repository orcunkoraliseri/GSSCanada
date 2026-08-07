import io
P = r"C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\9a0ff112-f2f7-4e19-b425-76397340666b\scratchpad\board.html"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:80])
    s = s.replace(old, new)

# ---- the J1 row: ready -> done, with the result ---------------------------
old_row = '''  ["V3-J1","Build the person-level retail check that was written down and then dropped","open","The audit's deliverable item 2, never built, never on any list. It is the check the exclusivity gate was mistakenly credited as being — and the only v3 task that could produce a new failure","ready · local, 418 MB pool on this machine",'''
new_row = '''  ["V3-J1","Build the person-level retail check that was written down and then dropped","done","BUILT, WIRED, AND IT FAILS. The generated shopping day is 1.8 % more like the person it was generated for than like a stranger's — against a 10 % bar written before the run, and a positive control that reads 238 %. Match the stranger on age, sex and work status and the 1.8 % becomes ZERO","closed today · 6 of 11 predictions held",'''
rep(old_row, new_row)

old_expl_tail = "<b>do not substitute a population average and call it person-level</b>, which is the defect this task exists to fix.\"],"
new_expl_tail = ("<b>do not substitute a population average and call it person-level</b>, which is the defect this task exists to fix."
 "<br><br><hr><b>RESULT, and it went against my prediction.</b> I wrote down beforehand that the model would retain the person, "
 "because it is <em>handed</em> that person's own observed shopping day as input. <b>It does not.</b> The check reads <b>+1.8 %</b> "
 "against a bar of <b>10 %</b> written before any number existed. <b>The bar was not moved.</b><br><br>"
 "<b>Five arms, eight of eight required conditions met — and the one that matters most is the positive control.</b> "
 "Replace each generated day with the person's own observed day and the check reads <b>+238 %</b>. So it can see person-level structure; "
 "on the shipped data it sees <b>0.75 % of that</b>. <b>Without that arm, a check reading zero is indistinguishable from a broken check</b>, "
 "and this whole result would have been unreadable.<br><br>"
 "🔴 <b>Then two pre-registered diagnostics made the finding bigger than the task.</b> The same statistic on the <em>work</em> channel reads "
 "<b>+55 %</b> — strongly person-specific, apparently. But tighten the comparison so the stranger also matches on age, sex and labour-force status, "
 "and <b>work collapses to +1.2 % and shopping to −0.02 %</b>. Work only looked personal because <em>whether you have a job at all</em> was free "
 "information. <b>So this is not a shopping defect. The generator reproduces groups, not individuals</b> — which is the same finding the audit made "
 "about the <em>checks</em>, now demonstrated about the <em>model</em>.<br><br>"
 "⚖️ <b>The counterargument, written down before the diagnostics ran rather than after.</b> Every respondent has <b>exactly one</b> observed diary day. "
 "So how much a person's Tuesday <em>should</em> predict their Saturday <b>cannot be measured from this data at all</b>. The check scores retention "
 "against <em>zero</em>, not against the truth — and if shopping really is near-independent across day types for one person, then zero is correct and "
 "the 10 % bar is wrong. <b>That limitation is printed beside the verdict, not filed behind it.</b><br><br>"
 "<b>Two defects in my own work, both caught before shipping.</b> My first wiring recorded the coverage line as a <em>pass</em> — putting a non-check "
 "into the scorecard's pass count, the exact thing forbidden last night for informational lines, committed by me an hour after quoting the rule. "
 "And the Step-4 checker turns out to carry <b>the same informational-line bug</b> that was fixed in Step 5 yesterday: it would crash on one. "
 "<b>Recorded and deliberately not fixed</b> — fixing it changes the scorecard, and this task was not a scorecard change.<br><br>"
 "<b>Stated rather than skipped:</b> the shipped Step-4 report was <b>not regenerated</b>. It is a cluster artefact and a local rerun would stamp it "
 "with this machine. <b>The check is in the code and is not yet in the shipped report.</b>\"],")
rep(old_expl_tail, new_expl_tail)

# ---- decision card 3 (X-3) gains the result -------------------------------
old_x3 = ("It is now <span class=\"mono\">V3-J1</span>, and it is the only v3 task with a real chance of producing a new failure.</span></li>")
new_x3 = ("It is now <span class=\"mono\">V3-J1</span> &mdash; <b>and as of today it is built, and it fails.</b><br><br>"
 "🔴 <b>You can now take this decision with the number in hand.</b> The generated shopping day is <b>1.8 %</b> more like the person it was generated for "
 "than like a stranger's, against a bar of <b>10 %</b> fixed before the run. Match the stranger on age, sex and work status and it is <b>zero</b>. "
 "The same test on the work channel behaves identically once matched. <b>The model reproduces groups, not individuals</b> &mdash; and the exclusivity "
 "check under discussion here was never going to detect that, at either severity.</span></li>")
rep(old_x3, new_x3)

# ---- header stamp ---------------------------------------------------------
rep("&middot; <b>6 v3 tasks: 3 your call, 3 ready</b>\n     &middot; v3 plan opened today, nothing executed",
    "&middot; <b>6 v3 tasks: 3 your call, 1 done, 2 ready</b>\n     &middot; <b>V3-J1 closed the same day it was written &mdash; and it failed</b>")

rep("<b>None of them clears a failure and none of them moves a band.</b></p>",
    "<b>None of them clears a failure and none of them moves a band.</b><br><br>"
    "🔴 <b>And the first v3 task is already closed &mdash; with a new failure.</b> The person-level check that was written down on 5 August and "
    "then dropped now exists. It says the generated shopping day carries <b>almost nothing</b> about the individual it was generated for; tighten "
    "the comparison by age, sex and work status and it carries <b>nothing at all</b>. The same is true of the work channel. <b>A new failure is not "
    "a reason to weaken a check</b>, and the bar it failed was written before the first number existed.</p>")

io.open(P, "w", encoding="utf-8").write(s)
print("patched j1")
