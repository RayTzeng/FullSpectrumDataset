#!/usr/bin/env python3
"""Builder for Stress17K/StressedSpeechASR template.jsonl.

Each concept is written as a pair: a no-listen phrasing and a listen phrasing.
`fmt` records whether the question spells out the ** convention (explicit) or
relies on it as the task default (implicit).

Stress17K differs from TinyStress in ways the wording has to respect:
  * every utterance carries exactly ONE stressed span, so the questions speak of
    "the stressed word" in the singular, never "every stressed word";
  * ~23% of spans cover several words (`**the play**`), so "word or phrase"
    appears wherever a phrase answer would otherwise contradict the question;
  * `text` is stored almost entirely in lower case, so no template asks for
    capitalisation or for "properly cased" output.

Wording rules for this task (from review):
  * The canonical instructions are "Based on the prosody in this recording, give
    the transcript with the stressed word in **." and "Transcribe the speech with
    the stressed word marked." They anchor the top of the weight range.
  * State the intent plainly. Every question must make the expected output
    determinable - in particular the cascade templates name the literal
    "Transcription:" / "Stressed:" line labels rather than gesturing at "two
    lines" or "below it".
  * No jargon for the stressed item: say "word", "word or phrase" or "part of the
    sentence", never "span", "focus", "pitch accent" or "prosodic prominence".
  * No slang or idiom for emphasis: no "hit hardest", "punched", "leaning on",
    "bit", "give it a spin".
"""
import json
import sys

MAIN = "text"
SPAN = "stressed_span(text)"
SPAN_Q = "stressed_span_quoted(text)"
SPAN_B = "stressed_span_bracketed(text)"
UPPER = "mark_upper(text)"
BRACK = "mark_brackets(text)"
EM = "mark_em(text)"
STAR = "mark_single_star(text)"
PLAIN = "plain_transcript(text)"
CASC_PLAIN = "cascade_plain_then_span(text)"
CASC_MARKED = "cascade_marked_then_span(text)"

TEMPLATES = []


def pair(group, fmt, answer, weight, no_listen, listen, listen_weight=None):
    """Add a concept as two templates: without and with an explicit listening cue."""
    lw = listen_weight if listen_weight is not None else round(max(weight - 0.05, 0.08), 2)
    TEMPLATES.append({"group": group, "fmt": fmt, "listen": False,
                      "question": no_listen, "answer": answer, "weight": weight})
    TEMPLATES.append({"group": group, "fmt": fmt, "listen": True,
                      "question": listen, "answer": answer, "weight": lw})


# ==================================================================== MAIN / DIRECT COMMANDS
pair("main/direct", "explicit", MAIN, 0.95,
     "Transcribe this utterance and wrap the stressed word in double asterisks.",
     "Listen to this audio and transcribe it, wrapping the stressed word in double asterisks.")
pair("main/direct", "explicit", MAIN, 0.95,
     "Give me the transcript with the emphasized word in **double asterisks**.",
     "Listen to the clip and give me the transcript with the emphasized word in **double asterisks**.")
pair("main/direct", "explicit", MAIN, 0.90,
     "Write out what is said, marking the emphasized word with **.",
     "Listen to the recording and write out what is said, marking the emphasized word with **.")
pair("main/direct", "explicit", MAIN, 0.90,
     "Write the transcript. Put ** around the word the speaker emphasizes.",
     "Listen to the audio. Write the transcript, putting ** around the word the speaker emphasizes.")
pair("main/direct", "explicit", MAIN, 0.85,
     "Transcribe the speech, using markdown bold (**word**) for the word the speaker stresses.",
     "Listen carefully, then transcribe the speech, using markdown bold (**word**) for the word the speaker stresses.")
pair("main/direct", "explicit", MAIN, 0.85,
     "Transcribe the sentence and bold the emphasized word, like **this**.",
     "After listening to the audio, transcribe the sentence and bold the emphasized word, like **this**.")
pair("main/direct", "explicit", MAIN, 0.80,
     "Exactly one word or phrase is stressed here. Transcribe the sentence and wrap that word in **.",
     "Listen to this clip. Exactly one word or phrase is stressed. Transcribe the sentence and wrap that word in **.")
pair("main/direct", "explicit", MAIN, 0.80,
     "Transcribe this utterance exactly as spoken, with ** around the stressed word.",
     "Listen to this utterance and transcribe it exactly as spoken, with ** around the stressed word.")
pair("main/direct", "explicit", MAIN, 0.75,
     "Transcribe and mark the sentence stress using **word** notation.",
     "Listen, then transcribe and mark the sentence stress using **word** notation.")
pair("main/direct", "explicit", MAIN, 0.70,
     "Turn this speech into text, keeping the emphasis visible with double asterisks around the stressed word.",
     "Listen to this speech and turn it into text, keeping the emphasis visible with double asterisks around the stressed word.")
pair("main/direct", "explicit", MAIN, 0.70,
     "Do a stress-aware transcription of this clip: unstressed words plain, the emphasized word wrapped in **.",
     "Listen to this clip and do a stress-aware transcription: unstressed words plain, the emphasized word wrapped in **.")
pair("main/direct", "explicit", MAIN, 0.70,
     "Transcribe the recording and put double asterisks around the word that receives the emphasis.",
     "Play the audio and transcribe it, putting double asterisks around the word that receives the emphasis.")
pair("main/direct", "explicit", MAIN, 0.65,
     "Write the utterance out in full, adding ** on both sides of the stressed word.",
     "Listen to the utterance and write it out in full, adding ** on both sides of the stressed word.")
pair("main/direct", "explicit", MAIN, 0.50,
     "Do ASR on this and mark the sentence stress inline (**word**).",
     "Listen to this, do ASR on it, and mark the sentence stress inline (**word**).")
pair("main/direct", "implicit", MAIN, 0.98,
     "Transcribe the speech with the stressed word marked.",
     "Listen to the speech and transcribe it with the stressed word marked.")
pair("main/direct", "implicit", MAIN, 0.98,
     "Transcribe the speech with the emphasized word marked.",
     "Listen to this recording and transcribe the speech with the emphasized word marked.")
pair("main/direct", "implicit", MAIN, 0.95,
     "Transcribe this utterance and mark the stressed word.",
     "Listen to this audio and transcribe it, marking the stressed word.")
pair("main/direct", "implicit", MAIN, 0.95,
     "Give me the transcript with the stressed word marked.",
     "Listen to the clip and give me the transcript with the stressed word marked.")
pair("main/direct", "implicit", MAIN, 0.90,
     "Transcribe the speech and indicate which word is emphasized.",
     "Listen to the speech, transcribe it, and indicate which word is emphasized.")
pair("main/direct", "implicit", MAIN, 0.85,
     "Transcribe this and show which word the speaker emphasizes.",
     "Listen to this and transcribe it, showing which word the speaker emphasizes.")
pair("main/direct", "implicit", MAIN, 0.85,
     "Write out the sentence with the emphasized word highlighted.",
     "After listening to the recording, write out the sentence with the emphasized word highlighted.")
pair("main/direct", "implicit", MAIN, 0.85,
     "Transcribe the audio and mark the word that receives the emphasis.",
     "Give the audio a listen, transcribe it, and mark the word that receives the emphasis.")
pair("main/direct", "implicit", MAIN, 0.80,
     "Produce a stress-marked transcript of this utterance.",
     "Listen to this utterance and produce a stress-marked transcript.")
pair("main/direct", "implicit", MAIN, 0.80,
     "Transcribe this clip with stress annotation.",
     "Listen to this clip and transcribe it with stress annotation.")
pair("main/direct", "implicit", MAIN, 0.75,
     "Give me a stress-annotated transcript of what is said here.",
     "Listen to the recording and give me a stress-annotated transcript of what is said.")

# ==================================================================== MAIN / WH-QUESTIONS
pair("main/wh", "explicit", MAIN, 0.90,
     "What is said here? Transcribe it with ** around the emphasized word.",
     "Listen to the recording. What is said here? Transcribe it with ** around the emphasized word.")
pair("main/wh", "explicit", MAIN, 0.90,
     "What does the speaker say, and which word do they stress? Give the transcript with the stressed word in **double asterisks**.",
     "Listen to this. What does the speaker say, and which word do they stress? Give the transcript with the stressed word in **double asterisks**.")
pair("main/wh", "explicit", MAIN, 0.80,
     "What are the words, and which one is emphasized? Write it as a transcript with ** markers.",
     "Listen closely: what are the words, and which one is emphasized? Write it as a transcript with ** markers.")
pair("main/wh", "explicit", MAIN, 0.70,
     "How would you transcribe this if you also marked the stressed word with double asterisks?",
     "How would you transcribe this after listening to it, marking the stressed word with double asterisks?")
pair("main/wh", "explicit", MAIN, 0.65,
     "What would a stress-marked transcript of this look like, using ** for the emphasized word?",
     "After listening, what would a stress-marked transcript of this look like, using ** for the emphasized word?")
pair("main/wh", "implicit", MAIN, 0.95,
     "What is being said, and which word is stressed?",
     "Listen to this clip. What is being said, and which word is stressed?")
pair("main/wh", "implicit", MAIN, 0.90,
     "What does the speaker say here? Mark the stressed word in your transcript.",
     "Listen to the audio. What does the speaker say? Mark the stressed word in your transcript.")
pair("main/wh", "implicit", MAIN, 0.85,
     "What are the exact words, and which one carries the emphasis?",
     "Listen and tell me the exact words and which one carries the emphasis.")
pair("main/wh", "implicit", MAIN, 0.80,
     "What is the sentence, with the emphasized word marked?",
     "After listening to this, what is the sentence, with the emphasized word marked?")
pair("main/wh", "implicit", MAIN, 0.80,
     "What is the transcript, and where does the emphasis fall?",
     "Listen to this and tell me the transcript and where the emphasis falls.")
pair("main/wh", "implicit", MAIN, 0.75,
     "Which words are spoken, and which one is stressed?",
     "Listen to the utterance: which words are spoken, and which one is stressed?")
pair("main/wh", "implicit", MAIN, 0.75,
     "How would you write this sentence out with the stressed word marked?",
     "Listen to it, then tell me how you would write this sentence out with the stressed word marked.")

# ==================================================================== MAIN / CAN-YOU
pair("main/canyou", "explicit", MAIN, 0.95,
     "Can you transcribe this and put ** around the stressed word?",
     "Can you listen to this and transcribe it, putting ** around the stressed word?")
pair("main/canyou", "explicit", MAIN, 0.85,
     "Could you write out this sentence with the emphasized word in **double asterisks**?",
     "Could you listen to this and write out the sentence with the emphasized word in **double asterisks**?")
pair("main/canyou", "explicit", MAIN, 0.80,
     "Are you able to transcribe this clip and bold the stressed word with **?",
     "Are you able to listen to this clip and transcribe it, bolding the stressed word with **?")
pair("main/canyou", "explicit", MAIN, 0.70,
     "Could you give me this as text with ** marking the emphasized word?",
     "Could you give this a listen and hand it back as text with ** marking the emphasized word?")
pair("main/canyou", "implicit", MAIN, 0.95,
     "Can you transcribe this and mark the stress?",
     "Can you listen to this and transcribe it, marking the stress?")
pair("main/canyou", "implicit", MAIN, 0.90,
     "Could you tell me what is said and which word is emphasized?",
     "Could you listen and tell me what is said and which word is emphasized?")
pair("main/canyou", "implicit", MAIN, 0.85,
     "Can you write down what they say, keeping the emphasized word marked?",
     "Can you give this a listen and write down what they say, keeping the emphasized word marked?")
pair("main/canyou", "implicit", MAIN, 0.80,
     "Would you be able to produce a stress-marked transcript of this?",
     "Would you be able to listen to this and produce a stress-marked transcript?")
pair("main/canyou", "implicit", MAIN, 0.75,
     "Can you transcribe this and point out where the stress falls?",
     "Have a listen - can you transcribe this and point out where the stress falls?")

# ==================================================================== MAIN / POLITE
pair("main/polite", "explicit", MAIN, 0.85,
     "Please transcribe this utterance, wrapping the stressed word in **.",
     "Please listen to this utterance and transcribe it, wrapping the stressed word in **.")
pair("main/polite", "explicit", MAIN, 0.70,
     "Would you please provide the transcript with the emphasized word marked as **word**?",
     "Would you please listen to this and provide the transcript with the emphasized word marked as **word**?")
pair("main/polite", "explicit", MAIN, 0.55,
     "I would appreciate a transcription of this clip with double asterisks around the stressed word.",
     "I would appreciate it if you listened to this clip and transcribed it with double asterisks around the stressed word.")
pair("main/polite", "explicit", MAIN, 0.50,
     "Kindly transcribe the utterance and put ** on either side of the stressed word.",
     "Kindly listen to the utterance, then transcribe it and put ** on either side of the stressed word.")
pair("main/polite", "implicit", MAIN, 0.85,
     "Please transcribe this and mark where the stress falls.",
     "Please listen to this and transcribe it, marking where the stress falls.")
pair("main/polite", "implicit", MAIN, 0.75,
     "Could you please tell me the words and which one is emphasized?",
     "Could you please listen to this recording and tell me the words and which one is emphasized?")
pair("main/polite", "implicit", MAIN, 0.60,
     "If you don't mind, I'd like the transcript with the stressed word indicated.",
     "If you don't mind, please listen to this and give me the transcript with the stressed word indicated.")
pair("main/polite", "implicit", MAIN, 0.55,
     "I'd be grateful for a stress-marked transcription of this utterance.",
     "I'd be grateful if you listened to this utterance and gave me a stress-marked transcription.")

# ==================================================================== MAIN / AUDIO-FRAMED
pair("main/audio", "explicit", MAIN, 0.95,
     "Based on the prosody in this recording, give the transcript with the stressed word in **.",
     "Listen to the prosody in this recording and give the transcript with the stressed word in **.")
pair("main/audio", "explicit", MAIN, 0.75,
     "From the audio alone, write the sentence with ** around the emphasized word.",
     "Listen to the audio and, from what you hear, write the sentence with ** around the emphasized word.")
pair("main/audio", "explicit", MAIN, 0.60,
     "Use the pitch and loudness cues in the clip to decide which word is stressed, then transcribe with ** markers.",
     "Listen for the pitch and loudness cues in the clip to decide which word is stressed, then transcribe with ** markers.")
pair("main/audio", "implicit", MAIN, 0.85,
     "Based on what you hear, transcribe this and mark the stressed word.",
     "Listen to this, and based on what you hear, transcribe it and mark the stressed word.")
pair("main/audio", "implicit", MAIN, 0.80,
     "This speaker emphasizes one word in the sentence. Transcribe it with that word marked.",
     "Listen to this speaker - they emphasize one word in the sentence. Transcribe it with that word marked.")
pair("main/audio", "implicit", MAIN, 0.75,
     "The recording carries a clear emphasis. Write the transcript so the emphasis is visible.",
     "Listen to the recording - it carries a clear emphasis. Write the transcript so the emphasis is visible.")
pair("main/audio", "implicit", MAIN, 0.70,
     "Pay attention to which word is spoken with extra emphasis, then transcribe with that word marked.",
     "Listen for the word spoken with extra emphasis, then transcribe with that word marked.")
pair("main/audio", "implicit", MAIN, 0.60,
     "Decide the stress from how the sentence is spoken, not from which word looks important in writing, then give the stress-marked transcript.",
     "Listen to how the sentence is spoken - not to which word looks important in writing - and give the stress-marked transcript.")

# ==================================================================== MAIN / WORKFLOW
pair("main/workflow", "explicit", MAIN, 0.65,
     "I am building a prosody dataset. Transcribe this clip and wrap the stressed word in double asterisks.",
     "I am building a prosody dataset. Listen to this clip, transcribe it, and wrap the stressed word in double asterisks.")
pair("main/workflow", "explicit", MAIN, 0.60,
     "For my annotation pipeline: transcript with the stressed word marked as **word**, please.",
     "For my annotation pipeline: listen to this and give me a transcript with the stressed word marked as **word**.")
pair("main/workflow", "explicit", MAIN, 0.55,
     "We are labeling sentence stress for a TTS study. Give the transcript with ** around the emphasized word.",
     "We are labeling sentence stress for a TTS study. Listen to this and give the transcript with ** around the emphasized word.")
pair("main/workflow", "explicit", MAIN, 0.45,
     "This clip goes into a stress-detection training set. Return the transcription with ** around the stressed word.",
     "This clip goes into a stress-detection training set. Listen to it and return the transcription with ** around the stressed word.")
pair("main/workflow", "implicit", MAIN, 0.60,
     "I am checking whether a TTS system placed the emphasis correctly. Transcribe this with the stressed word marked.",
     "I am checking whether a TTS system placed the emphasis correctly. Listen to this and transcribe it with the stressed word marked.")
pair("main/workflow", "implicit", MAIN, 0.55,
     "I am studying how emphasis changes meaning. Transcribe this one and mark the stressed word.",
     "I am studying how emphasis changes meaning. Listen to this one, transcribe it, and mark the stressed word.")
pair("main/workflow", "implicit", MAIN, 0.50,
     "I need stress annotations for a batch of utterances. Start with this one: transcript with the stressed word marked.",
     "I need stress annotations for a batch of utterances. Listen to this one and give me the transcript with the stressed word marked.")
pair("main/workflow", "implicit", MAIN, 0.45,
     "For a linguistics assignment on sentence stress, transcribe this utterance with the emphasized word marked.",
     "For a linguistics assignment on sentence stress, listen to this utterance and transcribe it with the emphasized word marked.")
pair("main/workflow", "implicit", MAIN, 0.40,
     "Quality-checking synthesized speech here. Give me the stress-marked transcript for this sample.",
     "Quality-checking synthesized speech here. Listen to this sample and give me the stress-marked transcript.")

# ==================================================================== MAIN / OUTPUT-CONSTRAINED
pair("main/output", "explicit", MAIN, 0.75,
     "Return only the transcript, with the stressed word wrapped in **. No commentary.",
     "Listen and return only the transcript, with the stressed word wrapped in **. No commentary.")
pair("main/output", "explicit", MAIN, 0.70,
     "Output a single line: the transcription with ** around the emphasized word.",
     "Listen to the clip and output a single line: the transcription with ** around the emphasized word.")
pair("main/output", "explicit", MAIN, 0.60,
     "Reply with the stress-marked transcript only - keep the ** markers, drop everything else.",
     "Listen to this and reply with the stress-marked transcript only - keep the ** markers, drop everything else.")
pair("main/output", "explicit", MAIN, 0.50,
     "Format: plain text, markdown bold on the stressed word, nothing before or after it.",
     "Listen first. Format: plain text, markdown bold on the stressed word, nothing before or after it.")
pair("main/output", "explicit", MAIN, 0.50,
     "Give me just the transcript with the stressed word in **. Do not explain what the emphasis means.",
     "Listen to the audio and give me just the transcript with the stressed word in **. Do not explain what the emphasis means.")
pair("main/output", "implicit", MAIN, 0.70,
     "Just the stress-marked transcript, nothing else.",
     "Listen to this - just the stress-marked transcript, nothing else.")
pair("main/output", "implicit", MAIN, 0.55,
     "One line, transcript with the stressed word marked, no preamble.",
     "Listen, then give me one line: transcript with the stressed word marked, no preamble.")

# ==================================================================== MAIN / CASUAL
pair("main/casual", "explicit", MAIN, 0.85,
     "Just transcribe it and put ** around the stressed word.",
     "Give it a listen and just transcribe it, putting ** around the stressed word.")
pair("main/casual", "explicit", MAIN, 0.75,
     "Type out what they said, with ** around the word they emphasize.",
     "Have a listen and type out what they said, with ** around the word they emphasize.")
pair("main/casual", "implicit", MAIN, 0.90,
     "What did they say, and which word did they stress?",
     "Give this a listen - what did they say, and which word did they stress?")
pair("main/casual", "implicit", MAIN, 0.85,
     "Write it down and mark the word they emphasize.",
     "Listen to this and write it down, marking the word they emphasize.")
pair("main/casual", "implicit", MAIN, 0.80,
     "Transcript please, with the stressed word marked.",
     "Quick listen - transcript please, with the stressed word marked.")
pair("main/casual", "implicit", MAIN, 0.75,
     "Tell me what's said and which word is stressed.",
     "Have a listen and tell me what's said and which word is stressed.")
pair("main/casual", "implicit", MAIN, 0.70,
     "Quick transcript with the stressed word marked, please.",
     "Listen to this one and give me a quick transcript with the stressed word marked.")

# ==================================================================== SPAN EXTRACTION
pair("span/wh", "implicit", SPAN, 0.95,
     "Which word or phrase does the speaker stress?",
     "Listen to this clip. Which word or phrase does the speaker stress?")
pair("span/wh", "implicit", SPAN, 0.95,
     "Which word is emphasized here?",
     "Listen to the audio - which word is emphasized?")
pair("span/wh", "implicit", SPAN, 0.90,
     "Which part of the sentence carries the stress?",
     "Listen and tell me which part of the sentence carries the stress.")
pair("span/wh", "implicit", SPAN, 0.85,
     "Where does the emphasis fall in this utterance?",
     "Listen to this utterance - where does the emphasis fall?")
pair("span/wh", "implicit", SPAN, 0.85,
     "Which words are spoken with extra emphasis?",
     "After listening, which words are spoken with extra emphasis?")
pair("span/wh", "implicit", SPAN, 0.80,
     "Which word receives the stress in this sentence?",
     "Listen to the sentence and tell me which word receives the stress.")
pair("span/wh", "implicit", SPAN, 0.80,
     "Which word does the speaker emphasize most?",
     "Give this a listen - which word does the speaker emphasize most?")
pair("span/direct", "implicit", SPAN, 0.90,
     "Identify the stressed word or phrase in this recording.",
     "Listen to this recording and identify the stressed word or phrase.")
pair("span/direct", "implicit", SPAN, 0.85,
     "Name the emphasized word in this sentence.",
     "Listen to the sentence and name the emphasized word.")
pair("span/direct", "implicit", SPAN, 0.80,
     "Pick out the word the speaker stresses.",
     "Listen carefully and pick out the word the speaker stresses.")
pair("span/direct", "implicit", SPAN, 0.75,
     "Tell me only the stressed word - not the whole sentence.",
     "Listen to this and tell me only the stressed word, not the whole sentence.")
pair("span/direct", "implicit", SPAN, 0.70,
     "Give the emphasized word from this utterance.",
     "Listen to this utterance and give the emphasized word.")
pair("span/canyou", "implicit", SPAN, 0.90,
     "Can you tell which word is stressed?",
     "Can you listen to this and tell which word is stressed?")
pair("span/canyou", "implicit", SPAN, 0.80,
     "Could you point out the emphasized word or phrase?",
     "Could you listen to this and point out the emphasized word or phrase?")
pair("span/canyou", "implicit", SPAN, 0.70,
     "Are you able to tell where the stress falls?",
     "Are you able to listen to this and tell where the stress falls?")
pair("span/polite", "implicit", SPAN, 0.65,
     "Please identify the stressed word or phrase.",
     "Please listen to this and identify the stressed word or phrase.")
pair("span/polite", "implicit", SPAN, 0.50,
     "I would appreciate it if you named the emphasized word in this clip.",
     "I would appreciate it if you listened to this clip and named the emphasized word.")
pair("span/output", "explicit", SPAN, 0.70,
     "Return only the stressed word or phrase, with no other text.",
     "Listen and return only the stressed word or phrase, with no other text.")
pair("span/output", "explicit", SPAN, 0.60,
     "Answer with the emphasized word alone - no transcript, no explanation.",
     "Listen to this and answer with the emphasized word alone - no transcript, no explanation.")
pair("span/workflow", "implicit", SPAN, 0.50,
     "I am collecting which word is stressed in each clip. Which one is it here?",
     "I am collecting which word is stressed in each clip. Listen to this one - which word is it?")
pair("span/workflow", "implicit", SPAN, 0.45,
     "For my stress-detection eval, report the emphasized word for this sample.",
     "For my stress-detection eval, listen to this sample and report the emphasized word.")
pair("span/casual", "implicit", SPAN, 0.85,
     "Which word did they stress?",
     "Have a listen - which word did they stress?")
pair("span/casual", "implicit", SPAN, 0.75,
     "Which word did they emphasize the most?",
     "Give it a listen - which word did they emphasize the most?")
pair("span/quoted", "explicit", SPAN_Q, 0.55,
     "Which word or phrase is stressed? Give it in double quotes.",
     "Listen to this. Which word or phrase is stressed? Give it in double quotes.")
pair("span/quoted", "explicit", SPAN_Q, 0.45,
     "Report the emphasized word as a quoted string.",
     "Listen to the clip and report the emphasized word as a quoted string.")
pair("span/bracketed", "explicit", SPAN_B, 0.40,
     "Which word is stressed? Wrap your answer in square brackets.",
     "Listen to this and tell me which word is stressed, wrapping your answer in square brackets.")
pair("span/bracketed", "explicit", SPAN_B, 0.30,
     "Give the stressed word or phrase in [square brackets].",
     "Listen and give the stressed word or phrase in [square brackets].")

# ==================================================================== ALTERNATIVE MARKUP
# These are not cosmetic casing variants: each question states its target
# notation outright, so they are clean instruction-following signal, and the
# conventions themselves (ALL CAPS, [brackets], <em>, *italics*) are all ones
# people genuinely use to write emphasis. They sit in the same band as the other
# format-specifying groups (main/output, cascade) rather than at the bottom.
pair("markup/upper", "explicit", UPPER, 0.72,
     "Transcribe this and write the stressed word in ALL CAPS instead of using asterisks.",
     "Listen to this and transcribe it, writing the stressed word in ALL CAPS instead of using asterisks.")
pair("markup/upper", "explicit", UPPER, 0.66,
     "Give me the transcript with the emphasized word capitalized, the rest as spoken.",
     "Listen to the audio and give me the transcript with the emphasized word capitalized, the rest as spoken.")
pair("markup/upper", "explicit", UPPER, 0.60,
     "Write out the sentence with the stressed word in uppercase.",
     "Listen to the sentence and write it out with the stressed word in uppercase.")
pair("markup/upper", "explicit", UPPER, 0.48,
     "Transcript please. Use uppercase, not markdown, to show which word is stressed.",
     "Listen first, then give me the transcript using uppercase, not markdown, to show which word is stressed.")
pair("markup/brackets", "explicit", BRACK, 0.68,
     "Transcribe this and put the stressed word or phrase in [square brackets].",
     "Listen to this and transcribe it, putting the stressed word or phrase in [square brackets].")
pair("markup/brackets", "explicit", BRACK, 0.62,
     "Give the transcript with square brackets around the emphasized word instead of asterisks.",
     "Listen to the clip and give the transcript with square brackets around the emphasized word instead of asterisks.")
pair("markup/brackets", "explicit", BRACK, 0.50,
     "My parser expects [brackets] for stress, not **. Transcribe accordingly.",
     "Listen to this and transcribe it - my parser expects [brackets] for stress, not **.")
pair("markup/em", "explicit", EM, 0.58,
     "Transcribe this and wrap the stressed word in <em> tags.",
     "Listen to this and transcribe it, wrapping the stressed word in <em> tags.")
pair("markup/em", "explicit", EM, 0.52,
     "I need the transcript as HTML, with the emphasized word inside <em>...</em>.",
     "Listen to the audio and give me the transcript as HTML, with the emphasized word inside <em>...</em>.")
pair("markup/em", "explicit", EM, 0.44,
     "Mark the stressed word with <em> tags and return the sentence.",
     "Listen, then mark the stressed word with <em> tags and return the sentence.")
pair("markup/star", "explicit", STAR, 0.58,
     "Transcribe this using single asterisks around the stressed word, not double.",
     "Listen to this and transcribe it using single asterisks around the stressed word, not double.")
pair("markup/star", "explicit", STAR, 0.52,
     "Give the transcript with *italic-style* markers on the emphasized word.",
     "Listen to the clip and give the transcript with *italic-style* markers on the emphasized word.")
pair("markup/star", "explicit", STAR, 0.44,
     "Use a single * on each side of the stressed word in your transcription.",
     "Listen to the audio, then transcribe it using a single * on each side of the stressed word.")

# ==================================================================== PLAIN TRANSCRIPT
pair("plain", "explicit", PLAIN, 0.60,
     "Transcribe this utterance as plain text - no stress markers.",
     "Listen to this utterance and transcribe it as plain text, with no stress markers.")
pair("plain", "explicit", PLAIN, 0.55,
     "Just the words, please - leave the emphasis unmarked.",
     "Listen to this and give me just the words, leaving the emphasis unmarked.")
pair("plain", "explicit", PLAIN, 0.45,
     "Give me an ordinary transcript of this clip, without marking the stress.",
     "Listen to this clip and give me an ordinary transcript, without marking the stress.")
pair("plain", "explicit", PLAIN, 0.35,
     "Transcribe the speech. Do not mark the stress - I only want the text.",
     "Listen to the speech and transcribe it. Do not mark the stress - I only want the text.")
pair("plain", "implicit", PLAIN, 0.55,
     "What is being said in this recording?",
     "Listen to this recording. What is being said?")
pair("plain", "implicit", PLAIN, 0.45,
     "Write down the sentence you hear.",
     "Listen to the audio and write down the sentence you hear.")

# ==================================================================== CASCADE
# Every cascade question names the literal "Transcription:" / "Stressed:" labels,
# so the two-line answer format is fully determined by the question.
pair("cascade/marked", "explicit", CASC_MARKED, 0.70,
     "Give two lines: \"Transcription:\" with the transcript, keeping the ** around the stressed word, then \"Stressed:\" with that word on its own.",
     "Listen to this and give two lines: \"Transcription:\" with the transcript, keeping the ** around the stressed word, then \"Stressed:\" with that word on its own.")
pair("cascade/marked", "explicit", CASC_MARKED, 0.60,
     "Answer in two labeled lines - \"Transcription:\" with the ** markers kept, and \"Stressed:\" with the emphasized word.",
     "Listen to the clip and answer in two labeled lines - \"Transcription:\" with the ** markers kept, and \"Stressed:\" with the emphasized word.")
pair("cascade/marked", "explicit", CASC_MARKED, 0.55,
     "Put the stress-marked transcript on a line starting \"Transcription:\", then the stressed word on a line starting \"Stressed:\".",
     "Listen to this, then put the stress-marked transcript on a line starting \"Transcription:\" and the stressed word on a line starting \"Stressed:\".")
pair("cascade/marked", "explicit", CASC_MARKED, 0.50,
     "Format your answer as a \"Transcription:\" line that keeps the ** markers, followed by a \"Stressed:\" line giving just the stressed word.",
     "Listen to the audio, then format your answer as a \"Transcription:\" line that keeps the ** markers, followed by a \"Stressed:\" line giving just the stressed word.")
pair("cascade/plain", "explicit", CASC_PLAIN, 0.70,
     "Give two lines: \"Transcription:\" with the plain text and no markers, then \"Stressed:\" with the emphasized word.",
     "Listen to this and give two lines: \"Transcription:\" with the plain text and no markers, then \"Stressed:\" with the emphasized word.")
pair("cascade/plain", "explicit", CASC_PLAIN, 0.60,
     "Answer as \"Transcription:\" followed by the unmarked sentence, then \"Stressed:\" followed by the stressed word.",
     "Listen to the audio, then answer as \"Transcription:\" followed by the unmarked sentence, then \"Stressed:\" followed by the stressed word.")
pair("cascade/plain", "explicit", CASC_PLAIN, 0.60,
     "What was said, and which word was stressed? Use two lines, labeled \"Transcription:\" and \"Stressed:\", with the transcript left unmarked.",
     "Listen to this: what was said, and which word was stressed? Use two lines, labeled \"Transcription:\" and \"Stressed:\", with the transcript left unmarked.")
pair("cascade/plain", "explicit", CASC_PLAIN, 0.55,
     "First line \"Transcription:\" with the sentence written out plainly, second line \"Stressed:\" with the word that was emphasized.",
     "Listen to the sentence, then give a first line \"Transcription:\" with it written out plainly and a second line \"Stressed:\" with the word that was emphasized.")
pair("cascade/plain", "explicit", CASC_PLAIN, 0.50,
     "Write the transcript without any markers on a \"Transcription:\" line, then name the stressed word on a \"Stressed:\" line.",
     "Listen to this, write the transcript without any markers on a \"Transcription:\" line, then name the stressed word on a \"Stressed:\" line.")
pair("cascade/plain", "explicit", CASC_PLAIN, 0.45,
     "Split your answer into a \"Transcription:\" line with the plain sentence and a \"Stressed:\" line with the emphasized word.",
     "Listen to the clip and split your answer into a \"Transcription:\" line with the plain sentence and a \"Stressed:\" line with the emphasized word.")


def main():
    verbose = "--groups" in sys.argv
    for t in TEMPLATES:
        out = {"question": t["question"], "answer": t["answer"], "weight": t["weight"]}
        if verbose:
            out = {"group": t["group"], "fmt": t["fmt"], "listen": t["listen"], **out}
        print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
