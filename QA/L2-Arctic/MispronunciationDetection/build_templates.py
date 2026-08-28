#!/usr/bin/env python3
"""Builder for L2-Arctic/MispronunciationDetection template.jsonl.

Each concept is written as a pair: a no-listen phrasing and a listen phrasing.
`fmt` marks whether the question spells out the output format (explicit) or
relies on the grouped-by-word default (implicit).

No template presupposes that errors exist: ~63% of generated pairs answer
"No mispronunciations detected." because the utterance carries no annotation.
"""
import json
import sys

GROUP = "group_by_word(mispronunciation)"          # C - default format
ARROW = "arrow_lines(mispronunciation)"            # B
WORDS = "mispronounced_words(mispronunciation)"    # D
PROSE = "prose_feedback(mispronunciation)"         # F

TEMPLATES = []


def pair(group, fmt, answer, weight, no_listen, listen, listen_weight=None):
    lw = listen_weight if listen_weight is not None else round(max(weight - 0.05, 0.08), 2)
    TEMPLATES.append({"group": group, "fmt": fmt, "listen": False,
                      "question": no_listen, "answer": answer, "weight": weight})
    TEMPLATES.append({"group": group, "fmt": fmt, "listen": True,
                      "question": listen, "answer": answer, "weight": lw})


# ============================================================ C / DIRECT COMMANDS
pair("group/direct", "explicit", GROUP, 0.85,
     "Identify the mispronounced phones in this recording. Give one line per word: `word: CANONICAL -> PRODUCED`.",
     "Listen to this recording and identify the mispronounced phones. Give one line per word: `word: CANONICAL -> PRODUCED`.")
pair("group/direct", "explicit", GROUP, 0.80,
     "List the pronunciation errors grouped by word, in the form `word: AE -> AA`, writing dropped phones as `X deleted` and added ones as `Y inserted`.",
     "Listen to the audio and list the pronunciation errors grouped by word, in the form `word: AE -> AA`, writing dropped phones as `X deleted` and added ones as `Y inserted`.")
pair("group/direct", "explicit", GROUP, 0.80,
     "Detect any mispronunciations and report them as `word: PHONE -> PHONE`, one word per line.",
     "Listen to this clip, detect any mispronunciations, and report them as `word: PHONE -> PHONE`, one word per line.")
pair("group/direct", "explicit", GROUP, 0.70,
     "Report the phone-level errors in ARPABET, grouped by word.",
     "Listen to the recording and report the phone-level errors in ARPABET, grouped by word.")
pair("group/direct", "explicit", GROUP, 0.70,
     "Go through this utterance and flag any phones the speaker pronounced wrong. One line per word: `word: canonical -> produced`.",
     "Listen through this utterance and flag any phones the speaker pronounced wrong. One line per word: `word: canonical -> produced`.")
pair("group/direct", "explicit", GROUP, 0.65,
     "Mark the pronunciation errors word by word. Deletions read `X deleted`, insertions read `Y inserted`.",
     "Listen to the audio and mark the pronunciation errors word by word. Deletions read `X deleted`, insertions read `Y inserted`.")
pair("group/direct", "explicit", GROUP, 0.70,
     "Give me the mispronunciation report: each mispronounced word on its own line as `word: expected -> produced`.",
     "Listen to this and give me the mispronunciation report: each mispronounced word on its own line as `word: expected -> produced`.")
pair("group/direct", "explicit", GROUP, 0.60,
     "Check this non-native speech for phone errors and list them by word, using ARPABET symbols.",
     "Listen to this non-native speech, check it for phone errors, and list them by word using ARPABET symbols.")
pair("group/direct", "explicit", GROUP, 0.60,
     "Produce a word-by-word list of pronunciation errors. Separate multiple errors on the same word with a semicolon.",
     "Listen to the clip and produce a word-by-word list of pronunciation errors. Separate multiple errors on the same word with a semicolon.")
pair("group/direct", "explicit", GROUP, 0.55,
     "Annotate the phone-level errors as `word: CANONICAL -> PERCEIVED`, one line per word, in ARPABET.",
     "Listen to the recording and annotate the phone-level errors as `word: CANONICAL -> PERCEIVED`, one line per word, in ARPABET.")
pair("group/direct", "implicit", GROUP, 0.95,
     "Identify any mispronunciations in this recording.",
     "Listen to this recording and identify any mispronunciations.")
pair("group/direct", "implicit", GROUP, 0.95,
     "List the pronunciation errors in this utterance, grouped by word.",
     "Listen to this utterance and list the pronunciation errors, grouped by word.")
pair("group/direct", "implicit", GROUP, 0.90,
     "Detect mispronunciations and report which words are affected and how.",
     "Listen to the audio, detect mispronunciations, and report which words are affected and how.")
pair("group/direct", "implicit", GROUP, 0.85,
     "Run mispronunciation detection on this clip.",
     "Listen to this clip and run mispronunciation detection on it.")
pair("group/direct", "implicit", GROUP, 0.85,
     "Report any phone-level pronunciation errors, word by word.",
     "Listen to the recording and report any phone-level pronunciation errors, word by word.")
pair("group/direct", "implicit", GROUP, 0.90,
     "Tell me which words this speaker mispronounced and what they said instead.",
     "Listen to this and tell me which words the speaker mispronounced and what they said instead.")
pair("group/direct", "implicit", GROUP, 0.85,
     "Find the pronunciation mistakes in this recording, if there are any.",
     "Listen to this recording and find the pronunciation mistakes, if there are any.")
pair("group/direct", "implicit", GROUP, 0.80,
     "Assess this speaker's pronunciation and list any errors by word.",
     "Listen to the speaker and assess their pronunciation, listing any errors by word.")
pair("group/direct", "implicit", GROUP, 0.85,
     "Point out any words that were pronounced incorrectly, and how.",
     "Listen to the clip and point out any words that were pronounced incorrectly, and how.")
pair("group/direct", "implicit", GROUP, 0.80,
     "Give me a mispronunciation breakdown for this utterance.",
     "Listen to this utterance and give me a mispronunciation breakdown.")

# ============================================================ C / WH-QUESTIONS
pair("group/wh", "explicit", GROUP, 0.80,
     "Which words are mispronounced, and which phones changed? Answer as `word: expected -> produced`, one per line.",
     "Listen to this. Which words are mispronounced, and which phones changed? Answer as `word: expected -> produced`, one per line.")
pair("group/wh", "explicit", GROUP, 0.75,
     "What pronunciation errors does this speaker make? List them by word in ARPABET.",
     "Listen to the recording. What pronunciation errors does this speaker make? List them by word in ARPABET.")
pair("group/wh", "explicit", GROUP, 0.70,
     "Which phones did the speaker substitute, drop, or add? Group them by word as `word: X -> Y`.",
     "Listen to the audio. Which phones did the speaker substitute, drop, or add? Group them by word as `word: X -> Y`.")
pair("group/wh", "explicit", GROUP, 0.55,
     "What does a phone-level error analysis of this clip look like? One line per word: `word: canonical -> produced`.",
     "After listening, what does a phone-level error analysis of this clip look like? One line per word: `word: canonical -> produced`.")
pair("group/wh", "explicit", GROUP, 0.55,
     "What errors would a pronunciation scorer flag here? Report `word: PHONE -> PHONE` per line.",
     "Listen to this clip. What errors would a pronunciation scorer flag? Report `word: PHONE -> PHONE` per line.")
pair("group/wh", "explicit", GROUP, 0.60,
     "Which words contain phone errors, and what are they? Use `word: expected -> produced`, with semicolons between multiple errors on one word.",
     "Listen and tell me which words contain phone errors and what they are. Use `word: expected -> produced`, with semicolons between multiple errors on one word.")
pair("group/wh", "implicit", GROUP, 0.95,
     "Which words did the speaker mispronounce, and how?",
     "Listen to this. Which words did the speaker mispronounce, and how?")
pair("group/wh", "implicit", GROUP, 0.85,
     "What did this speaker get wrong, pronunciation-wise?",
     "Listen to the recording. What did this speaker get wrong, pronunciation-wise?")
pair("group/wh", "implicit", GROUP, 0.85,
     "Where does the pronunciation go wrong in this utterance?",
     "Listen to this utterance. Where does the pronunciation go wrong?")
pair("group/wh", "implicit", GROUP, 0.90,
     "Are there any mispronunciations here? If so, which words and which phones?",
     "Listen to the clip. Are there any mispronunciations? If so, which words and which phones?")
pair("group/wh", "implicit", GROUP, 0.75,
     "How accurate is this speaker's pronunciation? List any word-level errors.",
     "Listen to the speaker. How accurate is their pronunciation? List any word-level errors.")
pair("group/wh", "implicit", GROUP, 0.80,
     "Which phones did the speaker miss, and in what words?",
     "Listen to this recording. Which phones did the speaker miss, and in what words?")
pair("group/wh", "implicit", GROUP, 0.70,
     "What pronunciation feedback would you give on this recording? List it by word.",
     "Listen to this recording. What pronunciation feedback would you give? List it by word.")

# ============================================================ C / CAN-YOU
pair("group/canyou", "explicit", GROUP, 0.80,
     "Can you list the mispronounced phones here, grouped by word as `word: X -> Y`?",
     "Can you listen to this and list the mispronounced phones, grouped by word as `word: X -> Y`?")
pair("group/canyou", "explicit", GROUP, 0.70,
     "Could you check this for pronunciation errors and report them as `word: canonical -> produced`?",
     "Could you listen to this, check it for pronunciation errors, and report them as `word: canonical -> produced`?")
pair("group/canyou", "explicit", GROUP, 0.60,
     "Can you run phone-level error detection and give me one line per mispronounced word?",
     "Can you listen to this, run phone-level error detection, and give me one line per mispronounced word?")
pair("group/canyou", "explicit", GROUP, 0.55,
     "Can you annotate the pronunciation errors word by word, in ARPABET?",
     "Can you listen to the audio and annotate the pronunciation errors word by word, in ARPABET?")
pair("group/canyou", "implicit", GROUP, 0.95,
     "Can you detect any mispronunciations in this recording?",
     "Can you listen to this recording and detect any mispronunciations?")
pair("group/canyou", "implicit", GROUP, 0.90,
     "Could you tell me which words were mispronounced and how?",
     "Could you listen to this and tell me which words were mispronounced and how?")
pair("group/canyou", "implicit", GROUP, 0.75,
     "Are you able to identify pronunciation errors in this speech?",
     "Are you able to listen to this speech and identify pronunciation errors?")
pair("group/canyou", "implicit", GROUP, 0.80,
     "I need to know which words this learner mispronounced - can you check?",
     "I need to know which words this learner mispronounced - can you give it a listen and check?")
pair("group/canyou", "implicit", GROUP, 0.75,
     "Would you mind checking this recording for pronunciation mistakes?",
     "Would you mind listening to this recording and checking it for pronunciation mistakes?")
pair("group/canyou", "implicit", GROUP, 0.80,
     "Help me spot the pronunciation errors in this clip.",
     "Listen to this clip and help me spot the pronunciation errors.")

# ============================================================ C / POLITE
pair("group/polite", "explicit", GROUP, 0.65,
     "Would you please list the pronunciation errors, grouped by word as `word: expected -> produced`?",
     "Would you please listen to this and list the pronunciation errors, grouped by word as `word: expected -> produced`?")
pair("group/polite", "explicit", GROUP, 0.50,
     "I would appreciate a phone-level error report for this clip, one line per mispronounced word.",
     "I would appreciate it if you listened to this clip and gave me a phone-level error report, one line per mispronounced word.")
pair("group/polite", "explicit", GROUP, 0.50,
     "Please provide the mispronunciation annotations grouped by word, using ARPABET phones.",
     "Please listen to the recording and provide the mispronunciation annotations grouped by word, using ARPABET phones.")
pair("group/polite", "explicit", GROUP, 0.55,
     "Please report each mispronounced word on its own line as `word: canonical -> produced`.",
     "Please listen to the audio and report each mispronounced word on its own line as `word: canonical -> produced`.")
pair("group/polite", "implicit", GROUP, 0.80,
     "Would you please identify any mispronunciations in this utterance?",
     "Would you please listen to this utterance and identify any mispronunciations?")
pair("group/polite", "implicit", GROUP, 0.60,
     "Kindly review this recording for pronunciation errors.",
     "Kindly listen to this recording and review it for pronunciation errors.")
pair("group/polite", "implicit", GROUP, 0.65,
     "If you don't mind, go through this and note any words that were mispronounced.",
     "If you don't mind, give this a listen and note any words that were mispronounced.")
pair("group/polite", "implicit", GROUP, 0.75,
     "Could I get a pronunciation error report for this recording, please?",
     "Could you listen to this recording and get me a pronunciation error report, please?")

# ============================================================ C / LISTEN-FRAMED
pair("group/listen", "explicit", GROUP, 0.70,
     "Report any phone-level errors by word: `word: X -> Y`.",
     "Listen for phone-level errors and report them by word: `word: X -> Y`.")
pair("group/listen", "explicit", GROUP, 0.60,
     "Produce a word-by-word pronunciation error list in ARPABET.",
     "Listen carefully and produce a word-by-word pronunciation error list in ARPABET.")
pair("group/listen", "explicit", GROUP, 0.60,
     "This is a learner recording. List any phone errors as `word: expected -> produced`.",
     "Listen to this learner recording and list any phone errors as `word: expected -> produced`.")
pair("group/listen", "explicit", GROUP, 0.55,
     "Compare what was produced against the canonical pronunciation and report the differences per word.",
     "Listen to the audio, compare what was produced against the canonical pronunciation, and report the differences per word.")
pair("group/listen", "implicit", GROUP, 0.75,
     "Pay attention to the speaker's articulation and note any mispronounced words.",
     "Listen closely to the speaker's articulation and note any mispronounced words.")
pair("group/listen", "implicit", GROUP, 0.75,
     "Attend to the articulation and list any words pronounced incorrectly.",
     "Listen closely to the articulation and list any words pronounced incorrectly.")
pair("group/listen", "implicit", GROUP, 0.80,
     "This is non-native English. Note any mispronunciations, word by word.",
     "Listen to this non-native English speech and note any mispronunciations, word by word.")
pair("group/listen", "implicit", GROUP, 0.70,
     "Check the speaker's pronunciation against standard American English and list any errors by word.",
     "Listen to the speaker and check their pronunciation against standard American English, listing any errors by word.")
pair("group/listen", "implicit", GROUP, 0.75,
     "Review this clip and tell me which words are pronounced incorrectly.",
     "Give this clip a careful listen and tell me which words are pronounced incorrectly.")

# ============================================================ C / WORKFLOW
pair("group/workflow", "explicit", GROUP, 0.45,
     "I'm building a pronunciation-feedback tool. Return the errors as `word: canonical -> produced`, one line per word.",
     "I'm building a pronunciation-feedback tool. Listen to this clip and return the errors as `word: canonical -> produced`, one line per word.")
pair("group/workflow", "explicit", GROUP, 0.45,
     "For our CALL system, output the phone errors grouped by word in ARPABET.",
     "For our CALL system, listen to this recording and output the phone errors grouped by word in ARPABET.")
pair("group/workflow", "explicit", GROUP, 0.40,
     "I'm annotating L2 speech. Please give the per-word phone errors as `word: X -> Y`.",
     "I'm annotating L2 speech. Please listen to this and give the per-word phone errors as `word: X -> Y`.")
pair("group/workflow", "explicit", GROUP, 0.45,
     "My pipeline expects one `word: expected -> produced` line per mispronounced word. Please check this clip for pronunciation errors.",
     "My pipeline expects one `word: expected -> produced` line per mispronounced word. Please listen to this clip and check its pronunciation.")
pair("group/workflow", "explicit", GROUP, 0.35,
     "For phonetics coursework, report the substitution, deletion, and addition errors by word.",
     "For phonetics coursework, listen to this recording and report the substitution, deletion, and addition errors by word.")
pair("group/workflow", "implicit", GROUP, 0.55,
     "I'm evaluating a mispronunciation detection model. Give me the reference errors for this clip.",
     "I'm evaluating a mispronunciation detection model. Listen to this clip and give me the reference errors.")
pair("group/workflow", "implicit", GROUP, 0.55,
     "We're scoring L2 English pronunciation. List the errors in this recording.",
     "We're scoring L2 English pronunciation. Listen to this recording and list the errors.")
pair("group/workflow", "implicit", GROUP, 0.50,
     "For a pronunciation-training app, tell me which words this learner needs to practice and why.",
     "For a pronunciation-training app, listen to this and tell me which words this learner needs to practice and why.")
pair("group/workflow", "implicit", GROUP, 0.50,
     "I'm preparing feedback for an English learner. What pronunciation errors are in this recording?",
     "I'm preparing feedback for an English learner. Listen to this recording - what pronunciation errors are in it?")
pair("group/workflow", "implicit", GROUP, 0.45,
     "We're building a pronunciation assessment dataset. Report the errors in this utterance.",
     "We're building a pronunciation assessment dataset. Listen to this utterance and report the errors.")
pair("group/workflow", "implicit", GROUP, 0.50,
     "I teach ESL and need to know which words this student pronounced incorrectly in this recording.",
     "I teach ESL - please listen to this recording and tell me which words this student pronounced incorrectly.")

# ============================================================ C / OUTPUT-CONSTRAINED
pair("group/constrained", "explicit", GROUP, 0.65,
     "Return only the pronunciation error lines, `word: canonical -> produced`, nothing else.",
     "Listen to the audio and return only the pronunciation error lines, `word: canonical -> produced`, nothing else.")
pair("group/constrained", "explicit", GROUP, 0.60,
     "One line per mispronounced word. No commentary.",
     "Listen to this and give one line per mispronounced word. No commentary.")
pair("group/constrained", "explicit", GROUP, 0.55,
     "Report every mispronounced word in this recording. Output format: `word: PHONE -> PHONE`, with `X deleted` and `Y inserted` for dropped and added phones. Nothing else.",
     "Listen to the clip and report every mispronounced word. Output format: `word: PHONE -> PHONE`, with `X deleted` and `Y inserted` for dropped and added phones. Nothing else.")
pair("group/constrained", "explicit", GROUP, 0.50,
     "List the pronunciation errors only, in ARPABET, one mispronounced word per line. If a word has several errors, join them with semicolons.",
     "Listen to the recording and list the pronunciation errors only, in ARPABET, one mispronounced word per line. If a word has several errors, join them with semicolons.")
pair("group/constrained", "explicit", GROUP, 0.50,
     "Plain text, one line for each mispronounced word: the word, a colon, then the phone change.",
     "Listen to the audio. Plain text, one line for each mispronounced word: the word, a colon, then the phone change.")
pair("group/constrained", "explicit", GROUP, 0.50,
     "Answer with the per-word pronunciation error list alone. Use ARPABET symbols.",
     "Listen to this and answer with the per-word pronunciation error list alone. Use ARPABET symbols.")
pair("group/constrained", "implicit", GROUP, 0.70,
     "Just the pronunciation errors, grouped by word. No explanation.",
     "Listen to the clip and give me just the pronunciation errors, grouped by word. No explanation.")
pair("group/constrained", "implicit", GROUP, 0.65,
     "Give me the pronunciation errors and nothing more.",
     "Listen to this and give me the pronunciation errors and nothing more.")
pair("group/constrained", "implicit", GROUP, 0.65,
     "Report the mispronunciations only - skip any preamble.",
     "Listen to the recording and report the mispronunciations only - skip any preamble.")

# ============================================================ C / CASUAL
pair("group/casual", "implicit", GROUP, 0.85,
     "What did they mispronounce here?",
     "Have a listen - what did they mispronounce here?")
pair("group/casual", "implicit", GROUP, 0.90,
     "Any pronunciation errors in this one?",
     "Give this a listen - any pronunciation errors?")
pair("group/casual", "implicit", GROUP, 0.80,
     "Where's the pronunciation off in this clip?",
     "Listen to this clip - where's the pronunciation off?")
pair("group/casual", "implicit", GROUP, 0.85,
     "Did they pronounce everything correctly? If not, which words?",
     "Listen to this. Did they pronounce everything correctly? If not, which words?")
pair("group/casual", "implicit", GROUP, 0.80,
     "Run a quick pronunciation check on this.",
     "Give this a quick listen and check the pronunciation.")
pair("group/casual", "implicit", GROUP, 0.80,
     "Anything wrong with how they pronounced this?",
     "Listen to the clip - anything wrong with how they pronounced it?")
pair("group/casual", "implicit", GROUP, 0.75,
     "How's their pronunciation here? List any words with errors.",
     "Listen to this - how's their pronunciation? List any words with errors.")
pair("group/casual", "explicit", GROUP, 0.65,
     "Quick check - which words were pronounced wrong? Use `word: expected -> produced`.",
     "Quick listen - which words were pronounced wrong? Use `word: expected -> produced`.")
pair("group/casual", "explicit", GROUP, 0.60,
     "Just list the mispronounced phones by word: `word: X -> Y`.",
     "Listen to this and just list the mispronounced phones by word: `word: X -> Y`.")
pair("group/casual", "explicit", GROUP, 0.60,
     "Quick one: per-word phone errors, `word: X -> Y`.",
     "Quick one - give it a listen and send the per-word phone errors, `word: X -> Y`.")

# ============================================================ C / REFERENCE-TEXT
pair("group/reftext", "explicit", GROUP, 0.70,
     "The speaker is reading: \"{text}\" Which phones did they get wrong? One line per word: `word: expected -> produced`.",
     "The speaker is reading: \"{text}\" Listen to the audio - which phones did they get wrong? One line per word: `word: expected -> produced`.")
pair("group/reftext", "explicit", GROUP, 0.60,
     "Reference text: \"{text}\" Report phone-level errors grouped by word, in ARPABET.",
     "Reference text: \"{text}\" Listen to the recording and report phone-level errors grouped by word, in ARPABET.")
pair("group/reftext", "explicit", GROUP, 0.55,
     "Compare the audio against this transcript - \"{text}\" - and list per-word phone errors as `word: X -> Y`.",
     "Listen to the audio, compare it against this transcript - \"{text}\" - and list per-word phone errors as `word: X -> Y`.")
pair("group/reftext", "explicit", GROUP, 0.50,
     "Given the reference \"{text}\", produce the mispronunciation annotations, one line per mispronounced word.",
     "Listen to the clip and, given the reference \"{text}\", produce the mispronunciation annotations, one line per mispronounced word.")
pair("group/reftext", "implicit", GROUP, 0.75,
     "Target sentence: \"{text}\" Identify any mispronunciations.",
     "Target sentence: \"{text}\" Listen to the recording and identify any mispronunciations.")
pair("group/reftext", "implicit", GROUP, 0.75,
     "The prompt was \"{text}\". Which words did the speaker mispronounce, and how?",
     "The prompt was \"{text}\". Listen to the audio - which words did the speaker mispronounce, and how?")
pair("group/reftext", "implicit", GROUP, 0.70,
     "They were asked to read \"{text}\". Check their pronunciation.",
     "They were asked to read \"{text}\". Listen to the recording and check their pronunciation.")
pair("group/reftext", "implicit", GROUP, 0.70,
     "Here's what they were supposed to say: \"{text}\" Which words did they pronounce wrong?",
     "Here's what they were supposed to say: \"{text}\" Listen to the clip - which words did they pronounce wrong?")
pair("group/reftext", "implicit", GROUP, 0.65,
     "The learner read \"{text}\". Where did their pronunciation deviate?",
     "The learner read \"{text}\". Listen to the audio - where did their pronunciation deviate?")
pair("group/reftext", "implicit", GROUP, 0.65,
     "Script: \"{text}\". Note any words pronounced incorrectly.",
     "Script: \"{text}\". Listen to the recording and note any words pronounced incorrectly.")

# ============================================================ B / ARROW LINES (typed, no timestamps)
pair("arrow", "explicit", ARROW, 0.60,
     "List every pronunciation error on its own line as `word: CANONICAL -> PRODUCED (error type)`.",
     "Listen to this and list every pronunciation error on its own line as `word: CANONICAL -> PRODUCED (error type)`.")
pair("arrow", "explicit", ARROW, 0.55,
     "Report each phone error separately, tagged by type: `word: X -> Y (substitution)`, `word: X deleted (deletion)`, `word: Y inserted (addition)`.",
     "Listen to the audio and report each phone error separately, tagged by type: `word: X -> Y (substitution)`, `word: X deleted (deletion)`, `word: Y inserted (addition)`.")
pair("arrow", "explicit", ARROW, 0.55,
     "Give me one line per pronunciation error, including the error type in parentheses.",
     "Listen to the clip and give me one line per pronunciation error, including the error type in parentheses.")
pair("arrow", "explicit", ARROW, 0.50,
     "Which pronunciation errors occurred? One per line, labeled substitution, deletion, or addition.",
     "Listen to this recording. Which pronunciation errors occurred? One per line, labeled substitution, deletion, or addition.")
pair("arrow", "explicit", ARROW, 0.50,
     "Detect the mispronunciations and classify each one. Format: `word: phone change (type)`, one error per line.",
     "Listen to the audio, detect the mispronunciations, and classify each one. Format: `word: phone change (type)`, one error per line.")
pair("arrow", "explicit", ARROW, 0.45,
     "I need each pronunciation error typed. Use `word: X -> Y (substitution)`, `word: X deleted (deletion)`, or `word: Y inserted (addition)`.",
     "Listen to this clip. I need each pronunciation error typed: `word: X -> Y (substitution)`, `word: X deleted (deletion)`, or `word: Y inserted (addition)`.")
pair("arrow", "explicit", ARROW, 0.45,
     "List the pronunciation errors with their categories, one per line - no timestamps.",
     "Listen to the recording and list the pronunciation errors with their categories, one per line - no timestamps.")
pair("arrow", "explicit", ARROW, 0.50,
     "For each phone error, give the word, the change, and whether it's a substitution, deletion, or addition.",
     "Listen to this and, for each phone error, give the word, the change, and whether it's a substitution, deletion, or addition.")
pair("arrow", "explicit", ARROW, 0.50,
     "Can you list every phone error separately, with its type in parentheses?",
     "Can you listen to this and list every phone error separately, with its type in parentheses?")
pair("arrow", "explicit", ARROW, 0.45,
     "Would you please report each pronunciation error on its own line, tagged with its error type?",
     "Would you please listen to this and report each pronunciation error on its own line, tagged with its error type?")
pair("arrow", "explicit", ARROW, 0.35,
     "For my error-type statistics, list each mispronunciation with its category: `word: X -> Y (substitution)`.",
     "For my error-type statistics, listen to this clip and list each mispronunciation with its category: `word: X -> Y (substitution)`.")
pair("arrow", "explicit", ARROW, 0.45,
     "Break the pronunciation errors out one per line and label each as substitution, deletion, or addition.",
     "Listen to the audio, break the pronunciation errors out one per line, and label each as substitution, deletion, or addition.")
pair("arrow", "explicit", ARROW, 0.45,
     "Quick list of pronunciation errors: word, phone change, and type.",
     "Give this a listen and send a quick list of pronunciation errors: word, phone change, and type.")
pair("arrow", "explicit", ARROW, 0.45,
     "Output one line per pronunciation error: `word: canonical -> produced (type)`. Nothing else.",
     "Listen to the clip and output one line per pronunciation error: `word: canonical -> produced (type)`. Nothing else.")
pair("arrow", "explicit", ARROW, 0.40,
     "The speaker read \"{text}\". List each phone error on its own line with its type.",
     "The speaker read \"{text}\". Listen to the audio and list each phone error on its own line with its type.")

# ============================================================ D / MISPRONOUNCED WORDS ONLY
pair("words", "explicit", WORDS, 0.55,
     "Which words did the speaker mispronounce? List just the words, comma-separated.",
     "Listen to this. Which words did the speaker mispronounce? List just the words, comma-separated.")
pair("words", "explicit", WORDS, 0.50,
     "Name the mispronounced words in this utterance, separated by commas.",
     "Listen to this utterance and name the mispronounced words, separated by commas.")
pair("words", "explicit", WORDS, 0.50,
     "I only need the mispronounced words, comma-separated - no phone details.",
     "Listen to the clip. I only need the mispronounced words, comma-separated - no phone details.")
pair("words", "explicit", WORDS, 0.45,
     "List the words containing pronunciation errors, in the order they are spoken.",
     "Listen to the recording and list the words containing pronunciation errors, in the order they are spoken.")
pair("words", "explicit", WORDS, 0.50,
     "Which words were pronounced incorrectly and need practice? Just the words, comma-separated.",
     "Listen to this - which words were pronounced incorrectly and need practice? Just the words, comma-separated.")
pair("words", "explicit", WORDS, 0.50,
     "Give me a comma-separated list of the mispronounced words.",
     "Listen to the audio and give me a comma-separated list of the mispronounced words.")
pair("words", "explicit", WORDS, 0.50,
     "Skip the phone details - which words were pronounced wrong? Comma-separated.",
     "Listen to this and skip the phone details - which words were pronounced wrong? Comma-separated.")
pair("words", "explicit", WORDS, 0.50,
     "Can you tell me which words were mispronounced? Words only, comma-separated.",
     "Can you listen to this and tell me which words were mispronounced? Words only, comma-separated.")
pair("words", "explicit", WORDS, 0.45,
     "Output only the mispronounced words, comma-separated. No error types, no timestamps.",
     "Listen to the recording and output only the mispronounced words, comma-separated. No error types, no timestamps.")
pair("words", "explicit", WORDS, 0.45,
     "Would you please list the words with pronunciation errors, comma-separated?",
     "Would you please listen to this and list the words with pronunciation errors, comma-separated?")
pair("words", "explicit", WORDS, 0.35,
     "For a vocabulary drill, tell me which words this learner mispronounced.",
     "For a vocabulary drill, listen to this recording and tell me which words this learner mispronounced.")
pair("words", "explicit", WORDS, 0.45,
     "Which words in this recording have phone errors? Comma-separated list.",
     "Listen to this recording. Which words have phone errors? Comma-separated list.")
pair("words", "explicit", WORDS, 0.50,
     "Any words pronounced incorrectly? Just name them, comma-separated.",
     "Give this a listen - any words pronounced incorrectly? Just name them, comma-separated.")
pair("words", "explicit", WORDS, 0.45,
     "The speaker read \"{text}\". Which of those words did they mispronounce? Comma-separated.",
     "The speaker read \"{text}\". Listen to the audio - which of those words did they mispronounce? Comma-separated.")
pair("words", "explicit", WORDS, 0.35,
     "I'm highlighting problem words in a transcript - which ones were mispronounced? Comma-separated.",
     "I'm highlighting problem words in a transcript. Listen to this clip - which ones were mispronounced? Comma-separated.")
pair("words", "explicit", WORDS, 0.45,
     "List the mispronounced words, comma-separated, in spoken order.",
     "Listen to the audio and list the mispronounced words, comma-separated, in spoken order.")
pair("words", "explicit", WORDS, 0.45,
     "Just the mispronounced words, please - comma-separated.",
     "Listen to this and give me just the mispronounced words - comma-separated.")

# ============================================================ F / PROSE FEEDBACK
pair("prose", "explicit", PROSE, 0.50,
     "Explain the pronunciation errors in full sentences.",
     "Listen to this recording and explain the pronunciation errors in full sentences.")
pair("prose", "explicit", PROSE, 0.50,
     "Describe the speaker's pronunciation errors in prose.",
     "Listen to the audio and describe the speaker's pronunciation errors in prose.")
pair("prose", "explicit", PROSE, 0.45,
     "Write feedback for this learner, explaining each pronunciation error in a sentence.",
     "Listen to this learner's recording and write feedback explaining each pronunciation error in a sentence.")
pair("prose", "explicit", PROSE, 0.45,
     "Summarize the phone errors in sentence form, one sentence per error.",
     "Listen to the clip and summarize the phone errors in sentence form, one sentence per error.")
pair("prose", "explicit", PROSE, 0.40,
     "How would you explain these pronunciation mistakes to the speaker? Use complete sentences.",
     "Listen to this. How would you explain the pronunciation mistakes to the speaker? Use complete sentences.")
pair("prose", "explicit", PROSE, 0.45,
     "Give me the pronunciation error analysis in prose rather than a list.",
     "Listen to the recording and give me the pronunciation error analysis in prose rather than a list.")
pair("prose", "explicit", PROSE, 0.45,
     "Could you describe each mispronunciation in a sentence?",
     "Could you listen to this and describe each mispronunciation in a sentence?")
pair("prose", "explicit", PROSE, 0.35,
     "I'm writing a feedback email to a student. Describe their pronunciation errors in sentences.",
     "I'm writing a feedback email to a student. Listen to this recording and describe their pronunciation errors in sentences.")
pair("prose", "explicit", PROSE, 0.45,
     "In plain sentences, what did this speaker mispronounce?",
     "Listen to this. In plain sentences, what did the speaker mispronounce?")
pair("prose", "explicit", PROSE, 0.40,
     "Write out the pronunciation errors as sentences, mentioning the word and the phones involved.",
     "Listen to the audio and write out the pronunciation errors as sentences, mentioning the word and the phones involved.")
pair("prose", "explicit", PROSE, 0.35,
     "Please explain, sentence by sentence, which phones were wrong in which words.",
     "Please listen to this and explain, sentence by sentence, which phones were wrong in which words.")
pair("prose", "explicit", PROSE, 0.35,
     "For a tutoring report, describe this speaker's pronunciation errors in prose.",
     "For a tutoring report, listen to this recording and describe the speaker's pronunciation errors in prose.")
pair("prose", "explicit", PROSE, 0.40,
     "Can you walk me through the pronunciation errors in sentence form?",
     "Can you listen to this and walk me through the pronunciation errors in sentence form?")
pair("prose", "explicit", PROSE, 0.35,
     "The learner read \"{text}\". Describe their pronunciation errors in complete sentences.",
     "The learner read \"{text}\". Listen to the recording and describe their pronunciation errors in complete sentences.")
pair("prose", "explicit", PROSE, 0.40,
     "Give the pronunciation errors as prose feedback, one sentence each.",
     "Listen to the clip and give the pronunciation errors as prose feedback, one sentence each.")


# --------------------------------------------------------------------------- #
# Reference-script framings
#
# L2-Arctic is read speech, so the prompt the speaker was given is known. These
# concepts state it in the question via {text}, the way a CALL system or a
# forced-alignment pipeline would supply the canonical transcript. Each entry
# names a concept by the start of its no-listen question; the framing is applied
# to BOTH variants of that concept so the pair stays aligned.
# --------------------------------------------------------------------------- #

SCRIPT_PLAN = [
    # ---- group/direct
    ("Identify the mispronounced phones", 'Script: "{text}".', "prefix"),
    ("Detect any mispronunciations and report them", 'The speaker is reading "{text}".', "prefix"),
    ("Report the phone-level errors in ARPABET", 'Reference text: "{text}".', "prefix"),
    ("List the pronunciation errors in this utterance", 'The prompt was "{text}".', "prefix"),
    ("Tell me which words this speaker mispronounced", 'They were asked to read "{text}".', "prefix"),
    ("Run mispronunciation detection on this clip", 'Target sentence: "{text}".', "prefix"),
    ("Give me the mispronunciation report", 'Expected transcript: "{text}".', "prefix"),
    ("Point out any words that were pronounced incorrectly", 'This clip should say "{text}".', "prefix"),
    # ---- group/wh
    ("Which words are mispronounced, and which phones changed", 'The sentence being read is "{text}".', "prefix"),
    ("What pronunciation errors does this speaker make", 'Prompt: "{text}".', "prefix"),
    ("Which words did the speaker mispronounce, and how", 'The speaker was given the line "{text}".', "prefix"),
    ("Where does the pronunciation go wrong", 'Canonical transcript: "{text}".', "prefix"),
    ("Which phones did the speaker miss", 'The intended utterance is "{text}".', "prefix"),
    # ---- group/canyou
    ("Can you detect any mispronunciations", 'Here is the reference sentence: "{text}".', "prefix"),
    ("Could you tell me which words were mispronounced", 'The text on the prompt card reads "{text}".', "prefix"),
    ("Can you list the mispronounced phones", 'Ground truth: "{text}".', "prefix"),
    ("I need to know which words this learner mispronounced", 'They are reading "{text}".', "prefix"),
    # ---- group/polite
    ("Would you please identify any mispronunciations", 'The reference transcript is "{text}".', "prefix"),
    ("Please provide the mispronunciation annotations", 'Script: "{text}".', "prefix"),
    ("Could I get a pronunciation error report", 'The recording is a reading of "{text}".', "prefix"),
    # ---- group/listen
    ("This is non-native English.", 'The script reads "{text}".', "prefix"),
    ("Check the speaker's pronunciation against standard", 'Reference text: "{text}".', "prefix"),
    ("This is a learner recording.", 'They were given the sentence "{text}".', "prefix"),
    # ---- group/workflow (framing trails the context sentence)
    ("I'm building a pronunciation-feedback tool", 'The reference text is "{text}".', "suffix"),
    ("We're scoring L2 English pronunciation", 'The script reads "{text}".', "suffix"),
    ("I'm preparing feedback for an English learner", 'They were reading "{text}".', "suffix"),
    ("I teach ESL and need to know which words", 'The prompt they read was "{text}".', "suffix"),
    # ---- group/constrained
    ("Return only the pronunciation error lines", 'Script: "{text}".', "prefix"),
    ("Just the pronunciation errors, grouped by word", 'The speaker is reading "{text}".', "prefix"),
    ("Report every mispronounced word in this recording", 'Reference: "{text}".', "prefix"),
    ("One line per mispronounced word. No commentary", 'Target sentence: "{text}".', "prefix"),
    # ---- group/casual
    ("Any pronunciation errors in this one", 'They are reading "{text}".', "prefix"),
    ("What did they mispronounce here", 'The line is "{text}".', "prefix"),
    ("Did they pronounce everything correctly", 'They were supposed to say "{text}".', "prefix"),
    ("Run a quick pronunciation check on this", 'Script: "{text}".', "prefix"),
    # ---- arrow
    ("List every pronunciation error on its own line", 'The prompt was "{text}".', "prefix"),
    ("Which pronunciation errors occurred", 'Reference text: "{text}".', "prefix"),
    ("For each phone error, give the word", 'The speaker is reading "{text}".', "prefix"),
    ("Detect the mispronunciations and classify each one", 'Expected transcript: "{text}".', "prefix"),
    ("Break the pronunciation errors out one per line", 'The intended sentence was "{text}".', "suffix"),
    # ---- words
    ("Which words did the speaker mispronounce? List just the words", 'They were asked to read "{text}".', "prefix"),
    ("Name the mispronounced words in this utterance", 'The prompt was "{text}".', "prefix"),
    ("Give me a comma-separated list of the mispronounced words", 'Script: "{text}".', "prefix"),
    ("List the mispronounced words, comma-separated, in spoken order", 'The canonical transcript is "{text}".', "suffix"),
    # ---- prose
    ("Explain the pronunciation errors in full sentences", 'The learner read "{text}".', "prefix"),
    ("Write feedback for this learner", 'The sentence they read was "{text}".', "suffix"),
]


def apply_script_framings():
    """Fold the reference script into both variants of each planned concept."""
    for key, framing, mode in SCRIPT_PLAN:
        hits = [i for i, t in enumerate(TEMPLATES)
                if not t["listen"] and t["question"].startswith(key)]
        if len(hits) != 1:
            raise SystemExit(
                f"SCRIPT_PLAN key matched {len(hits)} concepts (expected 1): {key!r}"
            )
        i = hits[0]
        if TEMPLATES[i + 1]["listen"] is not True:
            raise SystemExit(f"Concept at {i} is not followed by its listen variant: {key!r}")
        for j in (i, i + 1):
            q = TEMPLATES[j]["question"]
            if "{text}" in q:
                raise SystemExit(f"Concept already references the script: {key!r}")
            TEMPLATES[j]["question"] = (
                f"{framing} {q}" if mode == "prefix" else f"{q} {framing}"
            )
            TEMPLATES[j]["script"] = True


apply_script_framings()


def main():
    verbose = "--groups" in sys.argv
    for t in TEMPLATES:
        out = {"question": t["question"], "answer": t["answer"], "weight": t["weight"]}
        if verbose:
            out = {"group": t["group"], "fmt": t["fmt"], "listen": t["listen"], **out}
        print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
