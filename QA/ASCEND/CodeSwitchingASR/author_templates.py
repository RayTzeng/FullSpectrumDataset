#!/usr/bin/env python3
"""Author template.jsonl for ASCEND / CodeSwitchingASR."""
import json, sys

# (category, answer_expr, no_listen, listen)
A = []  # language-agnostic plain transcription
B = []  # language-conditioned
C = []  # cascade: language id + transcript
D = []  # output-constrained + casing variants

T = "text"

# ---------------------------------------------------------------- FAMILY A
A += [("direct", T, q, l) for q, l in [
 ("Transcribe this recording.", "Listen to this recording and transcribe it."),
 ("Write out exactly what the speaker says.", "Listen to the clip and write out exactly what the speaker says."),
 ("Transcribe this utterance word for word.", "Listen carefully and transcribe this utterance word for word."),
 ("Give me the transcript of this audio.", "Listen to the audio and give me its transcript."),
 ("Transcribe the speech in this clip.", "Play this clip, then transcribe the speech in it."),
 ("Produce a transcript for this conversational recording.", "Listen to this conversational recording and produce a transcript."),
 ("Write down what is said here.", "Listen and write down what is said here."),
 ("Transcribe this bilingual speech sample.", "Listen to this bilingual speech sample and transcribe it."),
 ("Convert this speech to text.", "Listen to the recording and convert the speech to text."),
 ("Transcribe the audio, keeping every word the speaker actually said.", "Listen through the audio and transcribe it, keeping every word the speaker actually said."),
 ("Give me a verbatim transcript.", "After listening, give me a verbatim transcript."),
 ("Transcribe this snippet of spontaneous conversation.", "Listen to this snippet of spontaneous conversation and transcribe it."),
 ("Write the spoken content of this file as text.", "Listen to this file and write its spoken content as text."),
 ("Transcribe the utterance, fillers and all.", "Listen to the utterance and transcribe it, fillers and all."),
]]
A += [("wh", T, q, l) for q, l in [
 ("What does the speaker say in this clip?", "Listen to this clip. What does the speaker say?"),
 ("What is being said here?", "Listen to the audio. What is being said here?"),
 ("What words are spoken in this recording?", "Listen to this recording. What words are spoken?"),
 ("How would you transcribe this?", "How would you transcribe this after listening to it?"),
 ("What's the transcript for this audio?", "Listen to the audio first. What's its transcript?"),
 ("What did they actually say?", "Give this a listen. What did they actually say?"),
 ("What is spoken in this utterance?", "Listen to this utterance. What is spoken in it?"),
 ("How does this utterance read as text?", "Listen to it, then tell me how this utterance reads as text."),
 ("What is the speaker's exact wording here?", "Listen closely. What is the speaker's exact wording here?"),
 ("What does this recording say, word for word?", "Listen to this recording. What does it say, word for word?"),
 ("Which words does the speaker produce in this clip?", "Listen to the clip and tell me which words the speaker produces."),
 ("What's on this recording, as text?", "Have a listen — what's on this recording, as text?"),
]]
A += [("canyou", T, q, l) for q, l in [
 ("Can you transcribe this?", "Can you listen to this and transcribe it?"),
 ("Could you write out what's said in this audio?", "Could you listen to this audio and write out what's said?"),
 ("Are you able to transcribe this conversational clip?", "Are you able to listen to this conversational clip and transcribe it?"),
 ("Can you give me the words spoken here?", "Can you listen and give me the words spoken here?"),
 ("Could you produce a transcript of this utterance?", "Could you listen to this utterance and produce a transcript?"),
 ("Can you turn this speech into text?", "Can you listen to the recording and turn the speech into text?"),
 ("Would you be able to transcribe this recording for me?", "Would you be able to listen to this recording and transcribe it for me?"),
 ("Can you tell me exactly what the speaker says?", "Can you listen and tell me exactly what the speaker says?"),
 ("Could you write down this utterance for me?", "Could you listen to this utterance and write it down for me?"),
 ("Can you handle this one and give me the transcript?", "Can you listen to this one and give me the transcript?"),
]]
A += [("polite", T, q, l) for q, l in [
 ("Please transcribe this recording.", "Please listen to this recording and transcribe it."),
 ("Would you please write out what is said in this clip?", "Would you please listen to this clip and write out what is said?"),
 ("I would appreciate a transcript of this audio.", "I would appreciate it if you listened to this audio and transcribed it."),
 ("Kindly transcribe the speech in this file.", "Kindly listen to this file and transcribe the speech in it."),
 ("If you don't mind, please give me the transcript here.", "If you don't mind, please listen and give me the transcript here."),
 ("I'd be grateful if you could transcribe this utterance.", "I'd be grateful if you could listen to this utterance and transcribe it."),
 ("Please write down the speaker's exact words.", "Please listen to the audio and write down the speaker's exact words."),
 ("Could I trouble you for a transcript of this clip?", "Could I trouble you to listen to this clip and transcribe it?"),
]]
A += [("workflow", T, q, l) for q, l in [
 ("I'm building a code-switching ASR benchmark. Please transcribe this recording.", "I'm building a code-switching ASR benchmark. Please listen to this recording and transcribe it."),
 ("I'm annotating a bilingual conversation corpus and need this clip transcribed.", "I'm annotating a bilingual conversation corpus — please listen to this clip and transcribe it."),
 ("For my speech dataset pipeline, transcribe this utterance.", "For my speech dataset pipeline, listen to this utterance and transcribe it."),
 ("I'm checking transcription quality on this corpus. What does this clip say?", "I'm checking transcription quality on this corpus. Listen to this clip — what does it say?"),
 ("We're evaluating an ASR model on spontaneous bilingual speech. Give me the reference transcript for this audio.", "We're evaluating an ASR model on spontaneous bilingual speech. Listen to this audio and give me its reference transcript."),
 ("I need this conversation segment written out for a research transcript.", "Please listen to this conversation segment and write it out for a research transcript."),
 ("Working on a bilingual speech study — transcribe this sample please.", "Working on a bilingual speech study — please listen to this sample and transcribe it."),
]]
A += [("casual", T, q, l) for q, l in [
 ("Just transcribe it.", "Give it a listen and just transcribe it."),
 ("What'd they say?", "Listen to this — what'd they say?"),
 ("Type out what's said.", "Listen and type out what's said."),
 ("Quick transcript please.", "Have a quick listen and give me the transcript."),
 ("Write it down, word for word.", "Listen, then write it down word for word."),
 ("So what's said in this one?", "Listen to this one — what's said?"),
 ("Just give me the words.", "Listen and just give me the words."),
]]

# ---------------------------------------------------------------- FAMILY B
B += [("direct", T, q, l) for q, l in [
 ("{language_clause} Transcribe it.", "{language_clause} Listen to it and transcribe it."),
 ("{language_note} Write out what is said.", "{language_note} Listen to the clip and write out what is said."),
 ("This recording is in {language_desc}. Give me the transcript.", "This recording is in {language_desc}. Listen to it and give me the transcript."),
 ("The speaker uses {language_desc} here. Transcribe the utterance.", "The speaker uses {language_desc} here. Listen and transcribe the utterance."),
 ("{language_clause} Produce a verbatim transcript.", "{language_clause} Listen through it and produce a verbatim transcript."),
 ("Transcribe this {language_adj} speech sample.", "Listen to this {language_adj} speech sample and transcribe it."),
 ("{language_note} Write down the exact wording.", "{language_note} Listen closely and write down the exact wording."),
 ("This clip contains {language_desc}. Convert it to text.", "This clip contains {language_desc}. Listen to it and convert it to text."),
 ("Transcribe the {language_desc} in this recording.", "Listen to this recording and transcribe the {language_desc} in it."),
]]
B += [("wh", T, q, l) for q, l in [
 ("{language_clause} What does the speaker say?", "{language_clause} Listen to it — what does the speaker say?"),
 ("This audio is in {language_desc}. What is being said?", "This audio is in {language_desc}. Listen and tell me what is being said."),
 ("{language_note} What are the exact words?", "{language_note} Listen carefully — what are the exact words?"),
 ("How would you transcribe this {language_adj} utterance?", "How would you transcribe this {language_adj} utterance after listening to it?"),
 ("The speech here is {language_desc}. What's the transcript?", "The speech here is {language_desc}. Listen to it — what's the transcript?"),
 ("{language_clause} What did they say, word for word?", "{language_clause} Give it a listen — what did they say, word for word?"),
 ("What does this {language_adj} clip say?", "Listen to this {language_adj} clip. What does it say?"),
]]
B += [("canyou", T, q, l) for q, l in [
 ("{language_clause} Can you transcribe it?", "{language_clause} Can you listen and transcribe it?"),
 ("Can you transcribe this {language_adj} recording?", "Can you listen to this {language_adj} recording and transcribe it?"),
 ("{language_note} Could you write out the utterance?", "{language_note} Could you listen and write out the utterance?"),
 ("This is {language_adj} speech — could you give me the transcript?", "This is {language_adj} speech — could you listen and give me the transcript?"),
 ("Are you able to transcribe {language_adj} speech? Here's a clip.", "Are you able to transcribe {language_adj} speech? Listen to this clip and try."),
 ("Can you handle this {language_adj} audio and write out what's said?", "Can you listen to this {language_adj} audio and write out what's said?"),
]]
B += [("polite", T, q, l) for q, l in [
 ("{language_clause} Please transcribe it.", "{language_clause} Please listen to it and transcribe it."),
 ("Please write out this {language_adj} utterance.", "Please listen to this {language_adj} utterance and write it out."),
 ("{language_note} I'd appreciate a full transcript.", "{language_note} Please listen through and give me a full transcript."),
 ("Would you please transcribe this {language_adj} clip?", "Would you please listen to this {language_adj} clip and transcribe it?"),
 ("Kindly give me the transcript of this {language_adj} recording.", "Kindly listen to this {language_adj} recording and give me its transcript."),
]]
B += [("workflow", T, q, l) for q, l in [
 ("I'm working on {language_adj} speech recognition. Transcribe this clip.", "I'm working on {language_adj} speech recognition. Listen to this clip and transcribe it."),
 ("{language_clause} I need it transcribed for a corpus study.", "{language_clause} Please listen and transcribe it for a corpus study."),
 ("For a bilingual conversation study: this sample is {language_desc}. Write out what's said.", "For a bilingual conversation study: this sample is {language_desc}. Listen to it and write out what's said."),
 ("{language_note} I'm building training data — give me the transcript.", "{language_note} I'm building training data — listen and give me the transcript."),
 ("Our ASR system struggles with {language_desc}. Transcribe this example.", "Our ASR system struggles with {language_desc}. Listen to this example and transcribe it."),
]]
B += [("casual", T, q, l) for q, l in [
 ("{language_clause} What'd they say?", "{language_clause} Have a listen — what'd they say?"),
 ("It's {language_desc}. Just transcribe it.", "It's {language_desc}. Give it a listen and just transcribe it."),
 ("{language_note} Just type out the words.", "{language_note} Listen and just type out the words."),
]]

# ---------------------------------------------------------------- FAMILY C
LAB = "format_cascade_labeled(language, text)"
SEN = "format_cascade_sentence(language, text)"
C += [("cascade_labeled", LAB, q, l) for q, l in [
 ("Identify the language or languages spoken, then transcribe the clip. Put the language on the first line as 'Language: ...' and the transcript on the second as 'Transcription: ...'.",
  "Listen to the clip, identify the language or languages spoken, then transcribe it. Put the language on the first line as 'Language: ...' and the transcript on the second as 'Transcription: ...'."),
 ("Tell me which language or languages this recording uses and what is said. Format it as two lines: 'Language: ...' then 'Transcription: ...'.",
  "Listen to this recording, then tell me which language or languages it uses and what is said. Format it as two lines: 'Language: ...' then 'Transcription: ...'."),
 ("For this audio, give me a 'Language:' line naming the language or languages used, followed by a 'Transcription:' line with the words spoken.",
  "Listen to this audio, then give me a 'Language:' line naming the language or languages used, followed by a 'Transcription:' line with the words spoken."),
 ("Work out whether this clip is Mandarin Chinese, English, or both, then transcribe it. Answer as 'Language: ...' on line one and 'Transcription: ...' on line two.",
  "Listen and work out whether this clip is Mandarin Chinese, English, or both, then transcribe it. Answer as 'Language: ...' on line one and 'Transcription: ...' on line two."),
 ("Label the language of this utterance and transcribe it, using a 'Language:' line and then a 'Transcription:' line.",
  "Listen to this utterance, label its language and transcribe it, using a 'Language:' line and then a 'Transcription:' line."),
 ("Can you identify the spoken language or languages and transcribe this clip? Use 'Language: ...' followed by 'Transcription: ...' on the next line.",
  "Can you listen to this clip, identify the spoken language or languages, and transcribe it? Use 'Language: ...' followed by 'Transcription: ...' on the next line."),
 ("Please report the language or languages in this recording on a 'Language:' line, then the verbatim transcript on a 'Transcription:' line.",
  "Please listen to this recording, report the language or languages on a 'Language:' line, then give the verbatim transcript on a 'Transcription:' line."),
 ("What language is this and what do they say? Give it as 'Language: ...' then 'Transcription: ...' on the next line.",
  "Listen to this. What language is it and what do they say? Give it as 'Language: ...' then 'Transcription: ...' on the next line."),
 ("I need both the language label and the transcript for this clip. Format: 'Language: ...' on one line, 'Transcription: ...' on the next.",
  "Listen to this clip — I need both the language label and the transcript. Format: 'Language: ...' on one line, 'Transcription: ...' on the next."),
 ("Run language identification and transcription on this audio. Return a 'Language:' line and a 'Transcription:' line.",
  "Listen to this audio, then run language identification and transcription on it. Return a 'Language:' line and a 'Transcription:' line."),
 ("Could you note the language or languages used here and then write out the speech? Put it as 'Language: ...' then 'Transcription: ...'.",
  "Could you listen, note the language or languages used here, and then write out the speech? Put it as 'Language: ...' then 'Transcription: ...'."),
 ("Give me a two-line answer for this recording: 'Language:' with the language or languages spoken, 'Transcription:' with the exact words.",
  "Listen to this recording and give me a two-line answer: 'Language:' with the language or languages spoken, 'Transcription:' with the exact words."),
 ("For my bilingual corpus I need language plus transcript per clip. Answer with 'Language: ...' on the first line and 'Transcription: ...' on the second.",
  "For my bilingual corpus I need language plus transcript per clip. Listen to this one and answer with 'Language: ...' on the first line and 'Transcription: ...' on the second."),
]]
C += [("cascade_sentence", SEN, q, l) for q, l in [
 ("Start with a sentence saying which language or languages the speaker uses, then give the transcript after 'Transcription:'.",
  "Listen to this clip. Start with a sentence saying which language or languages the speaker uses, then give the transcript after 'Transcription:'."),
 ("Say in a sentence what languages are spoken in this clip, then follow it with 'Transcription:' and the exact words.",
  "Listen to this clip, say in a sentence what languages are spoken, then follow it with 'Transcription:' and the exact words."),
 ("Describe the language or languages used in one sentence, then append 'Transcription:' and the verbatim transcript.",
  "Listen to the audio, describe the language or languages used in one sentence, then append 'Transcription:' and the verbatim transcript."),
 ("Can you state which language or languages the speaker uses as a sentence, then give 'Transcription:' followed by what they said?",
  "Can you listen, state which language or languages the speaker uses as a sentence, then give 'Transcription:' followed by what they said?"),
 ("Please open with a sentence naming the language or languages in this recording, then write 'Transcription:' and the transcript.",
  "Please listen to this recording, open with a sentence naming the language or languages, then write 'Transcription:' and the transcript."),
 ("First a sentence about which language or languages the speaker is using, then 'Transcription:' with the words. Do that for this clip.",
  "Listen to this clip. First a sentence about which language or languages the speaker is using, then 'Transcription:' with the words."),
 ("Tell me in a sentence what language or languages this speaker uses, then give the transcript after a 'Transcription:' marker.",
  "Listen and tell me in a sentence what language or languages this speaker uses, then give the transcript after a 'Transcription:' marker."),
 ("I want a sentence identifying the spoken language or languages, followed by 'Transcription:' and the exact wording.",
  "Listen to this audio. I want a sentence identifying the spoken language or languages, followed by 'Transcription:' and the exact wording."),
 ("Could you write one sentence on the language or languages heard here, then 'Transcription:' and the full transcript?",
  "Could you listen, write one sentence on the language or languages heard here, then 'Transcription:' and the full transcript?"),
 ("Answer with a sentence naming the language or languages, then 'Transcription:' plus what is said in this utterance.",
  "Listen to this utterance and answer with a sentence naming the language or languages, then 'Transcription:' plus what is said."),
 ("For this clip: one sentence on the language or languages the speaker uses, then 'Transcription:' and the words.",
  "Listen to this clip, then give one sentence on the language or languages the speaker uses, then 'Transcription:' and the words."),
 ("Give a sentence about which languages appear in this audio, then 'Transcription:' followed by the transcript.",
  "Listen to this audio, give a sentence about which languages appear in it, then 'Transcription:' followed by the transcript."),
]]

# ---------------------------------------------------------------- FAMILY D
D += [("constrained", T, q, l) for q, l in [
 ("Transcribe this recording. Return only the transcript text — no commentary.", "Listen to this recording and transcribe it. Return only the transcript text — no commentary."),
 ("Give me the transcript on a single line, nothing else.", "Listen to the audio and give me the transcript on a single line, nothing else."),
 ("Transcribe this utterance exactly as spoken. Don't add punctuation.", "Listen to this utterance and transcribe it exactly as spoken. Don't add punctuation."),
 ("Write out the speech. Output the transcript alone, with no preamble.", "Listen to the clip and write out the speech. Output the transcript alone, with no preamble."),
 ("Transcribe this clip and return just the words — no timestamps, no speaker labels.", "Listen to this clip and transcribe it, returning just the words — no timestamps, no speaker labels."),
 ("Give me the raw transcript for this audio, unpunctuated, on one line.", "Listen to this audio and give me its raw transcript, unpunctuated, on one line."),
 ("Transcribe the utterance. Don't clean up the disfluencies — keep them in.", "Listen to the utterance and transcribe it. Don't clean up the disfluencies — keep them in."),
 ("Output only what was said. No explanation, no formatting.", "Listen to the recording and output only what was said. No explanation, no formatting."),
 ("Transcribe this recording verbatim, including hesitations and fillers, and return nothing but the transcript.", "Listen to this recording and transcribe it verbatim, including hesitations and fillers, returning nothing but the transcript."),
]]
D += [("casing", "text.lower()", q, l) for q, l in [
 ("Transcribe this and give the result in all lowercase.", "Listen to this and transcribe it, giving the result in all lowercase."),
 ("Transcribe this clip, then lowercase the whole transcript.", "Listen to this clip, transcribe it, then lowercase the whole transcript."),
 ("Transcribe this utterance and normalize the output to lowercase.", "Listen to this utterance, transcribe it, and normalize the output to lowercase."),
]]
D += [("casing", "text.upper()", q, l) for q, l in [
 ("Give me the transcript of this audio in ALL CAPS.", "Listen to this audio and give me its transcript in ALL CAPS."),
 ("Transcribe this and return the transcript in uppercase.", "Listen to this and transcribe it, returning the transcript in uppercase."),
 ("Can you transcribe this and put the transcript in all caps?", "Can you listen to this, transcribe it, and put the transcript in all caps?"),
]]

# ---------------------------------------------------------------- weights
BASE = {
 ("A", "direct"): 0.88, ("A", "wh"): 0.90, ("A", "canyou"): 0.86, ("A", "polite"): 0.72,
 ("A", "workflow"): 0.55, ("A", "casual"): 0.80,
 ("B", "direct"): 0.70, ("B", "wh"): 0.72, ("B", "canyou"): 0.68, ("B", "polite"): 0.58,
 ("B", "workflow"): 0.45, ("B", "casual"): 0.62,
 ("C", "cascade_labeled"): 0.50, ("C", "cascade_sentence"): 0.42,
 ("D", "constrained"): 0.55, ("D", "casing"): 0.12,
}
JITTER = [0.0, -0.04, 0.03, -0.02, 0.05, -0.03, 0.02, -0.05, 0.04, -0.01]

out = []
for fam, concepts in (("A", A), ("B", B), ("C", C), ("D", D)):
    for i, (cat, ans, q_no, q_yes) in enumerate(concepts):
        base = BASE[(fam, cat)]
        w = round(max(0.05, base + JITTER[i % len(JITTER)]), 3)
        wl = round(max(0.05, w - 0.03), 3)
        cid = f"csasr_ascend_{fam.lower()}_{cat}_{i:03d}"
        out.append({"template_id": cid + "_nolisten", "question_template": q_no,
                    "answer_template": ans, "weight": w})
        out.append({"template_id": cid + "_listen", "question_template": q_yes,
                    "answer_template": ans, "weight": wl})

dest = sys.argv[1]
with open(dest, "w", encoding="utf-8") as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print(f"wrote {len(out)} templates -> {dest}")
