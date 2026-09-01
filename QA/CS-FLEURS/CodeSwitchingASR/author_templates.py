#!/usr/bin/env python3
"""Author template.jsonl for CS-FLEURS / CodeSwitchingASR.

Placeholders are language-PAIR agnostic: they are rendered from the entry's
`language` code, never from an assumption that English is one of the members.
  {language_pair}       'Spanish-English'
  {language_list}       'Spanish and English'
  {matrix_language}     'Spanish'   (first code)
  {embedded_language}   'English'   (second code)
"""
import json, sys

A, B, C, D, E = [], [], [], [], []
T = "clean(text)"

# ---------------------------------------------------------------- FAMILY A  (pair-agnostic)
A += [("direct", T, q, l) for q, l in [
 ("Transcribe this code-switched utterance.", "Listen to this code-switched utterance and transcribe it."),
 ("Write out everything the speaker says.", "Listen to the recording and write out everything the speaker says."),
 ("Give me the transcript of this audio.", "Listen to this audio and give me its transcript."),
 ("Transcribe this sentence exactly as spoken.", "Listen to this sentence and transcribe it exactly as spoken."),
 ("Produce a verbatim transcript of this recording.", "Listen through this recording and produce a verbatim transcript."),
 ("Transcribe the mixed-language speech in this clip.", "Listen to this clip and transcribe the mixed-language speech in it."),
 ("Convert this utterance into written text.", "Listen to this utterance and convert it into written text."),
 ("Transcribe this recording, preserving every word across both languages.", "Listen to this recording and transcribe it, preserving every word across both languages."),
 ("Write down the spoken sentence.", "Listen to the audio and write down the spoken sentence."),
 ("Transcribe this multilingual speech sample.", "Listen to this multilingual speech sample and transcribe it."),
 ("Give me a full transcript for this clip.", "Listen to this clip and give me a full transcript."),
 ("Transcribe the audio, switching scripts wherever the speaker switches languages.", "Listen to the audio and transcribe it, switching scripts wherever the speaker switches languages."),
]]
A += [("wh", T, q, l) for q, l in [
 ("What does the speaker say in this recording?", "Listen to this recording. What does the speaker say?"),
 ("What is said in this clip?", "Listen to the clip. What is said in it?"),
 ("How would you transcribe this utterance?", "How would you transcribe this utterance after listening to it?"),
 ("What's the transcript of this audio?", "Listen to the audio first. What's its transcript?"),
 ("What sentence is spoken here?", "Listen to this. What sentence is spoken here?"),
 ("What are the exact words in this recording?", "Listen closely. What are the exact words in this recording?"),
 ("How does this spoken sentence read in writing?", "Listen to it, then tell me how this spoken sentence reads in writing."),
 ("What does this clip say, word for word?", "Listen to this clip. What does it say, word for word?"),
 ("Which words does the speaker produce here?", "Listen and tell me which words the speaker produces here."),
 ("What is the written form of this utterance?", "Listen to this utterance. What is its written form?"),
]]
A += [("canyou", T, q, l) for q, l in [
 ("Can you transcribe this?", "Can you listen to this and transcribe it?"),
 ("Could you write out what's said in this recording?", "Could you listen to this recording and write out what's said?"),
 ("Are you able to transcribe this code-switched clip?", "Are you able to listen to this code-switched clip and transcribe it?"),
 ("Can you give me the words spoken in this audio?", "Can you listen and give me the words spoken in this audio?"),
 ("Could you produce a transcript of this sentence?", "Could you listen to this sentence and produce a transcript?"),
 ("Can you turn this speech into text?", "Can you listen to this speech and turn it into text?"),
 ("Would you be able to transcribe this mixed-language recording?", "Would you be able to listen to this mixed-language recording and transcribe it?"),
 ("Can you tell me exactly what is said here?", "Can you listen and tell me exactly what is said here?"),
 ("Could you write down this utterance for me?", "Could you listen to this utterance and write it down for me?"),
]]
A += [("polite", T, q, l) for q, l in [
 ("Please transcribe this recording.", "Please listen to this recording and transcribe it."),
 ("Would you please write out what is said in this clip?", "Would you please listen to this clip and write out what is said?"),
 ("I would appreciate a transcript of this audio.", "I would appreciate it if you listened to this audio and transcribed it."),
 ("Kindly transcribe this utterance.", "Kindly listen to this utterance and transcribe it."),
 ("If you don't mind, please give me the transcript for this clip.", "If you don't mind, please listen to this clip and give me its transcript."),
 ("I'd be grateful if you could transcribe this sentence.", "I'd be grateful if you could listen to this sentence and transcribe it."),
 ("Please write out the speaker's exact words.", "Please listen to the audio and write out the speaker's exact words."),
]]
A += [("workflow", T, q, l) for q, l in [
 ("I'm evaluating a code-switching ASR system. Please transcribe this recording.", "I'm evaluating a code-switching ASR system. Please listen to this recording and transcribe it."),
 ("I'm assembling a multilingual speech corpus and need this clip transcribed.", "I'm assembling a multilingual speech corpus — please listen to this clip and transcribe it."),
 ("For my ASR training pipeline, transcribe this utterance.", "For my ASR training pipeline, listen to this utterance and transcribe it."),
 ("I'm checking reference transcripts on this dataset. What does this clip say?", "I'm checking reference transcripts on this dataset. Listen to this clip — what does it say?"),
 ("We benchmark models on intra-sentential code-switching. Give me the transcript for this audio.", "We benchmark models on intra-sentential code-switching. Listen to this audio and give me its transcript."),
 ("I need this sample written out for a code-switching study.", "Please listen to this sample and write it out for a code-switching study."),
]]
A += [("casual", T, q, l) for q, l in [
 ("Just transcribe it.", "Give it a listen and just transcribe it."),
 ("What'd they say?", "Listen to this — what'd they say?"),
 ("Type out what's said.", "Listen and type out what's said."),
 ("Transcript please.", "Have a listen and give me the transcript."),
 ("Write out the sentence, word for word.", "Listen, then write out the sentence word for word."),
 ("Just give me the words.", "Listen and just give me the words."),
]]

# ---------------------------------------------------------------- FAMILY B  (pair-conditioned)
B += [("direct", T, q, l) for q, l in [
 ("This clip code-switches between {language_list}. Transcribe it.", "This clip code-switches between {language_list}. Listen to it and transcribe it."),
 ("The speaker mixes {language_list} here. Write out what is said.", "The speaker mixes {language_list} here. Listen and write out what is said."),
 ("This is {language_pair} code-switched speech. Give me the transcript.", "This is {language_pair} code-switched speech. Listen to it and give me the transcript."),
 ("Transcribe this {language_pair} recording.", "Listen to this {language_pair} recording and transcribe it."),
 ("The languages in this utterance are {language_list}. Produce a verbatim transcript.", "The languages in this utterance are {language_list}. Listen through it and produce a verbatim transcript."),
 ("This audio mixes {language_list}. Convert it to text.", "This audio mixes {language_list}. Listen to it and convert it to text."),
 ("Transcribe this sample of {language_pair} code-switching.", "Listen to this sample of {language_pair} code-switching and transcribe it."),
 ("The speaker alternates between {language_list} in this clip. Write down the exact wording.", "The speaker alternates between {language_list} in this clip. Listen closely and write down the exact wording."),
 ("This recording contains both {language_list}. Transcribe the whole utterance.", "This recording contains both {language_list}. Listen to it and transcribe the whole utterance."),
]]
B += [("wh", T, q, l) for q, l in [
 ("This clip mixes {language_list}. What does the speaker say?", "This clip mixes {language_list}. Listen to it — what does the speaker say?"),
 ("The speech here is {language_pair} code-switched. What is being said?", "The speech here is {language_pair} code-switched. Listen and tell me what is being said."),
 ("How would you transcribe this {language_pair} utterance?", "How would you transcribe this {language_pair} utterance after listening to it?"),
 ("This sample alternates between {language_list}. What's the transcript?", "This sample alternates between {language_list}. Listen to it — what's the transcript?"),
 ("What does this {language_pair} clip say, word for word?", "Listen to this {language_pair} clip. What does it say, word for word?"),
 ("The speaker switches between {language_list}. What are the exact words?", "The speaker switches between {language_list}. Listen carefully — what are the exact words?"),
 ("What sentence is spoken in this {language_pair} recording?", "Listen to this {language_pair} recording. What sentence is spoken?"),
]]
B += [("canyou", T, q, l) for q, l in [
 ("This clip code-switches between {language_list}. Can you transcribe it?", "This clip code-switches between {language_list}. Can you listen and transcribe it?"),
 ("Can you transcribe this {language_pair} recording?", "Can you listen to this {language_pair} recording and transcribe it?"),
 ("The speaker uses {language_list} here — could you write out the utterance?", "The speaker uses {language_list} here — could you listen and write it out?"),
 ("This is {language_pair} speech. Could you give me the transcript?", "This is {language_pair} speech. Could you listen and give me the transcript?"),
 ("Are you able to handle {language_pair} code-switching? Here's a clip to transcribe.", "Are you able to handle {language_pair} code-switching? Listen to this clip and transcribe it."),
 ("Can you transcribe this audio? It mixes {language_list}.", "Can you listen to this audio and transcribe it? It mixes {language_list}."),
]]
B += [("polite", T, q, l) for q, l in [
 ("This clip mixes {language_list}. Please transcribe it.", "This clip mixes {language_list}. Please listen to it and transcribe it."),
 ("Please write out this {language_pair} utterance.", "Please listen to this {language_pair} utterance and write it out."),
 ("The languages here are {language_list}. I'd appreciate a full transcript.", "The languages here are {language_list}. Please listen through and give me a full transcript."),
 ("Would you please transcribe this {language_pair} clip?", "Would you please listen to this {language_pair} clip and transcribe it?"),
 ("Kindly give me the transcript of this {language_pair} recording.", "Kindly listen to this {language_pair} recording and give me its transcript."),
]]
B += [("workflow", T, q, l) for q, l in [
 ("I'm working on {language_pair} speech recognition. Transcribe this clip.", "I'm working on {language_pair} speech recognition. Listen to this clip and transcribe it."),
 ("This sample code-switches between {language_list}. I need it transcribed for a corpus study.", "This sample code-switches between {language_list}. Please listen and transcribe it for a corpus study."),
 ("For a multilingual ASR evaluation: this clip is {language_pair}. Write out what's said.", "For a multilingual ASR evaluation: this clip is {language_pair}. Listen to it and write out what's said."),
 ("I'm building {language_pair} training data — give me the transcript for this audio.", "I'm building {language_pair} training data — listen to this audio and give me its transcript."),
 ("Our model struggles when speakers switch between {language_list}. Transcribe this example.", "Our model struggles when speakers switch between {language_list}. Listen to this example and transcribe it."),
]]
B += [("casual", T, q, l) for q, l in [
 ("It's {language_pair}. Just transcribe it.", "It's {language_pair}. Give it a listen and just transcribe it."),
 ("They're switching between {language_list} — what'd they say?", "They're switching between {language_list} — have a listen, what'd they say?"),
 ("{language_pair} clip. Just type out the words.", "{language_pair} clip. Listen and just type out the words."),
]]

# ---------------------------------------------------------------- FAMILY C  (cascade)
LAB = "format_cascade_labeled(language, text)"
SEN = "format_cascade_sentence(language, text)"
C += [("cascade_labeled", LAB, q, l) for q, l in [
 ("Identify the pair of languages being mixed, then transcribe the clip. Put the pair on the first line as 'Language pair: ...' and the transcript on the second as 'Transcription: ...'.",
  "Listen to the clip, identify the pair of languages being mixed, then transcribe it. Put the pair on the first line as 'Language pair: ...' and the transcript on the second as 'Transcription: ...'."),
 ("Tell me which two languages this recording mixes and what is said. Format it as two lines: 'Language pair: ...' then 'Transcription: ...'.",
  "Listen to this recording, then tell me which two languages it mixes and what is said. Format it as two lines: 'Language pair: ...' then 'Transcription: ...'."),
 ("For this audio, give me a 'Language pair:' line naming the two languages, followed by a 'Transcription:' line with the words spoken.",
  "Listen to this audio, then give me a 'Language pair:' line naming the two languages, followed by a 'Transcription:' line with the words spoken."),
 ("Work out which languages the speaker is code-switching between, then transcribe. Answer as 'Language pair: ...' on line one and 'Transcription: ...' on line two.",
  "Listen and work out which languages the speaker is code-switching between, then transcribe. Answer as 'Language pair: ...' on line one and 'Transcription: ...' on line two."),
 ("Label the language pair of this utterance and transcribe it, using a 'Language pair:' line and then a 'Transcription:' line.",
  "Listen to this utterance, label its language pair and transcribe it, using a 'Language pair:' line and then a 'Transcription:' line."),
 ("Can you identify the two spoken languages and transcribe this clip? Use 'Language pair: ...' followed by 'Transcription: ...' on the next line.",
  "Can you listen to this clip, identify the two spoken languages, and transcribe it? Use 'Language pair: ...' followed by 'Transcription: ...' on the next line."),
 ("Please report the language pair in this recording on a 'Language pair:' line, then the verbatim transcript on a 'Transcription:' line.",
  "Please listen to this recording, report the language pair on a 'Language pair:' line, then give the verbatim transcript on a 'Transcription:' line."),
 ("Which languages are mixed here, and what is said? Give it as 'Language pair: ...' then 'Transcription: ...' on the next line.",
  "Listen to this. Which languages are mixed here, and what is said? Give it as 'Language pair: ...' then 'Transcription: ...' on the next line."),
 ("I need both the language pair and the transcript for this clip. Format: 'Language pair: ...' on one line, 'Transcription: ...' on the next.",
  "Listen to this clip — I need both the language pair and the transcript. Format: 'Language pair: ...' on one line, 'Transcription: ...' on the next."),
 ("Run language-pair identification and transcription on this audio. Return a 'Language pair:' line and a 'Transcription:' line.",
  "Listen to this audio, then run language-pair identification and transcription on it. Return a 'Language pair:' line and a 'Transcription:' line."),
 ("Could you note which languages are combined here and then write out the speech? Put it as 'Language pair: ...' then 'Transcription: ...'.",
  "Could you listen, note which languages are combined here, and then write out the speech? Put it as 'Language pair: ...' then 'Transcription: ...'."),
 ("Give me a two-line answer for this recording: 'Language pair:' with the languages mixed, 'Transcription:' with the exact words.",
  "Listen to this recording and give me a two-line answer: 'Language pair:' with the languages mixed, 'Transcription:' with the exact words."),
]]
C += [("cascade_sentence", SEN, q, l) for q, l in [
 ("Start with a sentence saying which languages the speaker mixes, then give the transcript after 'Transcription:'.",
  "Listen to this clip. Start with a sentence saying which languages the speaker mixes, then give the transcript after 'Transcription:'."),
 ("Say in a sentence what languages are combined in this clip, then follow it with 'Transcription:' and the exact words.",
  "Listen to this clip, say in a sentence what languages are combined, then follow it with 'Transcription:' and the exact words."),
 ("Describe the language pair in one sentence, then append 'Transcription:' and the verbatim transcript.",
  "Listen to the audio, describe the language pair in one sentence, then append 'Transcription:' and the verbatim transcript."),
 ("Can you state which languages the speaker switches between as a sentence, then give 'Transcription:' followed by what they said?",
  "Can you listen, state which languages the speaker switches between as a sentence, then give 'Transcription:' followed by what they said?"),
 ("Please open with a sentence naming the language pair in this recording, then write 'Transcription:' and the transcript.",
  "Please listen to this recording, open with a sentence naming the language pair, then write 'Transcription:' and the transcript."),
 ("First a sentence about which languages are being mixed, then 'Transcription:' with the words. Do that for this clip.",
  "Listen to this clip. First a sentence about which languages are being mixed, then 'Transcription:' with the words."),
 ("Tell me in a sentence which languages this speaker combines, then give the transcript after a 'Transcription:' marker.",
  "Listen and tell me in a sentence which languages this speaker combines, then give the transcript after a 'Transcription:' marker."),
 ("I want a sentence identifying the language pair, followed by 'Transcription:' and the exact wording.",
  "Listen to this audio. I want a sentence identifying the language pair, followed by 'Transcription:' and the exact wording."),
 ("Could you write one sentence on which languages are mixed here, then 'Transcription:' and the full transcript?",
  "Could you listen, write one sentence on which languages are mixed here, then 'Transcription:' and the full transcript?"),
 ("Answer with a sentence naming the two languages, then 'Transcription:' plus what is said in this utterance.",
  "Listen to this utterance and answer with a sentence naming the two languages, then 'Transcription:' plus what is said."),
 ("For this clip: one sentence on the languages the speaker mixes, then 'Transcription:' and the words.",
  "Listen to this clip, then give one sentence on the languages the speaker mixes, then 'Transcription:' and the words."),
 ("Give a sentence about which languages appear in this audio, then 'Transcription:' followed by the transcript.",
  "Listen to this audio, give a sentence about which languages appear in it, then 'Transcription:' followed by the transcript."),
]]

# ---------------------------------------------------------------- FAMILY D  (constrained / casing)
D += [("constrained", T, q, l) for q, l in [
 ("Transcribe this recording. Return only the transcript text — no commentary.", "Listen to this recording and transcribe it. Return only the transcript text — no commentary."),
 ("Transcribe this utterance, keeping the original punctuation and spacing exactly as they appear in the speech.", "Listen to this utterance and transcribe it, keeping the original punctuation and spacing exactly as they appear in the speech."),
 ("Give me the transcript for this clip and nothing else.", "Listen to this clip and give me its transcript and nothing else."),
 ("Write out the speech. Output the transcript alone, with no preamble.", "Listen to the audio and write out the speech. Output the transcript alone, with no preamble."),
 ("Transcribe this clip and return just the words — no timestamps, no language tags.", "Listen to this clip and transcribe it, returning just the words — no timestamps, no language tags."),
 ("Transcribe this audio without translating any part of it — keep each word in the language it was spoken in.", "Listen to this audio and transcribe it without translating any part of it — keep each word in the language it was spoken in."),
 ("Transcribe the utterance and keep the punctuation the reference uses. Don't normalize it.", "Listen to the utterance, transcribe it, and keep the punctuation the reference uses. Don't normalize it."),
 ("Output only what was said. No explanation, no formatting.", "Listen to the recording and output only what was said. No explanation, no formatting."),
]]
D += [("casing", "clean(text).lower()", q, l) for q, l in [
 ("Transcribe this and give the result in all lowercase.", "Listen to this and transcribe it, giving the result in all lowercase."),
 ("Transcribe this clip, then lowercase the whole transcript.", "Listen to this clip, transcribe it, then lowercase the whole transcript."),
 ("Transcribe this utterance and normalize the output to lowercase.", "Listen to this utterance, transcribe it, and normalize the output to lowercase."),
]]
D += [("casing", "clean(text).upper()", q, l) for q, l in [
 ("Give me the transcript of this audio in ALL CAPS.", "Listen to this audio and give me its transcript in ALL CAPS."),
 ("Transcribe this and return the transcript in uppercase.", "Listen to this and transcribe it, returning the transcript in uppercase."),
 ("Can you transcribe this and put the transcript in all caps?", "Can you listen to this, transcribe it, and put the transcript in all caps?"),
]]

# ---------------------------------------------------------------- FAMILY E  (marker-annotated; gated)
E += [("marked", "text", q, l) for q, l in [
 ("Transcribe this clip and wrap every {embedded_language} span in double asterisks, like **this**. Leave the {matrix_language} text unmarked.",
  "Listen to this clip and transcribe it, wrapping every {embedded_language} span in double asterisks, like **this**. Leave the {matrix_language} text unmarked."),
 ("Write out what is said, marking each stretch of {embedded_language} by surrounding it with ** on both sides.",
  "Listen to the audio and write out what is said, marking each stretch of {embedded_language} by surrounding it with ** on both sides."),
 ("Give me the transcript of this {language_pair} utterance with the {embedded_language} words emphasised in Markdown (**word**).",
  "Listen to this {language_pair} utterance and give me its transcript with the {embedded_language} words emphasised in Markdown (**word**)."),
 ("Transcribe this recording, using **double asterisks** around any {embedded_language} that appears in it.",
  "Listen to this recording and transcribe it, using **double asterisks** around any {embedded_language} that appears in it."),
 ("Can you transcribe this and highlight the {embedded_language} portions by wrapping each one in **?",
  "Can you listen to this, transcribe it, and highlight the {embedded_language} portions by wrapping each one in **?"),
 ("Please transcribe this clip and put ** before and after every {embedded_language} word or phrase.",
  "Please listen to this clip, transcribe it, and put ** before and after every {embedded_language} word or phrase."),
 ("I need a transcript where the {embedded_language} insertions are flagged with **double asterisks**. Do that for this audio.",
  "Listen to this audio, then give me a transcript where the {embedded_language} insertions are flagged with **double asterisks**."),
 ("Transcribe the utterance and mark the code-switch points by bolding the {embedded_language} spans with ** on each side.",
  "Listen to the utterance, transcribe it, and mark the code-switch points by bolding the {embedded_language} spans with ** on each side."),
 ("Could you write out this {language_pair} speech with each {embedded_language} segment wrapped in **?",
  "Could you listen to this {language_pair} speech and write it out with each {embedded_language} segment wrapped in **?"),
 ("For my code-switch annotation pass: transcribe this clip and surround every {embedded_language} token with **.",
  "For my code-switch annotation pass: listen to this clip, transcribe it, and surround every {embedded_language} token with **."),
 ("Transcribe this and use **asterisk pairs** to delimit the {embedded_language} spans so the switch boundaries are visible.",
  "Listen to this and transcribe it, using **asterisk pairs** to delimit the {embedded_language} spans so the switch boundaries are visible."),
 ("Write the transcript for this recording, marking {embedded_language} with ** and leaving {matrix_language} plain.",
  "Listen to this recording and write its transcript, marking {embedded_language} with ** and leaving {matrix_language} plain."),
]]

# ---------------------------------------------------------------- weights
BASE = {
 ("A", "direct"): 0.88, ("A", "wh"): 0.90, ("A", "canyou"): 0.86, ("A", "polite"): 0.72,
 ("A", "workflow"): 0.55, ("A", "casual"): 0.80,
 ("B", "direct"): 0.70, ("B", "wh"): 0.72, ("B", "canyou"): 0.68, ("B", "polite"): 0.58,
 ("B", "workflow"): 0.45, ("B", "casual"): 0.62,
 ("C", "cascade_labeled"): 0.50, ("C", "cascade_sentence"): 0.42,
 ("D", "constrained"): 0.55, ("D", "casing"): 0.12,
 ("E", "marked"): 0.15,
}
JITTER = [0.0, -0.04, 0.03, -0.02, 0.05, -0.03, 0.02, -0.05, 0.04, -0.01]

out = []
for fam, concepts in (("A", A), ("B", B), ("C", C), ("D", D), ("E", E)):
    for i, (cat, ans, q_no, q_yes) in enumerate(concepts):
        base = BASE[(fam, cat)]
        w = round(max(0.05, base + (JITTER[i % len(JITTER)] if cat != "marked" else JITTER[i % len(JITTER)] * 0.4)), 3)
        wl = round(max(0.05, w - 0.03), 3)
        cid = f"csasr_csfleurs_{fam.lower()}_{cat}_{i:03d}"
        rec_no = {"template_id": cid + "_nolisten", "question_template": q_no,
                  "answer_template": ans, "weight": w}
        rec_yes = {"template_id": cid + "_listen", "question_template": q_yes,
                   "answer_template": ans, "weight": wl}
        if fam == "E":
            rec_no["requires"] = "has_markers"
            rec_yes["requires"] = "has_markers"
        out.append(rec_no); out.append(rec_yes)

dest = sys.argv[1]
with open(dest, "w", encoding="utf-8") as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print(f"wrote {len(out)} templates -> {dest}")
