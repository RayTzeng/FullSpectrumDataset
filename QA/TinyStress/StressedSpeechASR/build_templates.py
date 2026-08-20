#!/usr/bin/env python3
"""Builder for TinyStress/StressedSpeechASR template.jsonl.

Each concept is written as a pair: a no-listen phrasing and a listen phrasing.
`fmt` records whether the question spells out the ** convention (explicit) or
relies on it as the task default (implicit).
"""
import json
import sys

MAIN = "text"
LIST = "stressed_words(text)"
LISTB = "stressed_words_bracketed(text)"
UPPER = "mark_upper(text)"
BRACK = "mark_brackets(text)"
EM = "mark_em(text)"
STAR = "mark_single_star(text)"
CASC_PLAIN = "cascade_plain_then_stress(text)"
CASC_MARKED = "cascade_marked_then_stress(text)"

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
     "Transcribe this utterance and wrap each stressed word in double asterisks.",
     "Listen to this audio and transcribe it, wrapping each stressed word in double asterisks.")
pair("main/direct", "explicit", MAIN, 0.90,
     "Write out what is said, marking the emphasized words with **.",
     "Listen to the recording and write out what is said, marking the emphasized words with **.")
pair("main/direct", "explicit", MAIN, 0.85,
     "Transcribe the speech, using markdown bold (**word**) for any word the speaker stresses.",
     "Listen carefully, then transcribe the speech, using markdown bold (**word**) for any word the speaker stresses.")
pair("main/direct", "explicit", MAIN, 0.95,
     "Give me the transcript with the stressed words in **double asterisks**.",
     "Give the clip a listen and hand me the transcript with the stressed words in **double asterisks**.")
pair("main/direct", "explicit", MAIN, 0.85,
     "Transcribe the sentence and bold the words that carry emphasis, like **this**.",
     "After listening to the audio, transcribe the sentence and bold the words that carry emphasis, like **this**.")
pair("main/direct", "explicit", MAIN, 0.70,
     "Do a stress-aware transcription of this clip: normal words plain, emphasized words wrapped in **.",
     "Listen to this clip and do a stress-aware transcription: normal words plain, emphasized words wrapped in **.")
pair("main/direct", "explicit", MAIN, 0.90,
     "Write the transcript. Put ** around every word the speaker emphasizes.",
     "Listen to the audio. Write the transcript, putting ** around every word the speaker emphasizes.")
pair("main/direct", "explicit", MAIN, 0.75,
     "Transcribe and mark sentence stress with **word** notation.",
     "Listen, then transcribe and mark sentence stress with **word** notation.")
pair("main/direct", "explicit", MAIN, 0.75,
     "Transcribe this utterance exactly as spoken and wrap every stressed word in ** - there may be more than one.",
     "Listen to this utterance, transcribe it exactly as spoken, and wrap every stressed word in ** - there may be more than one.")
pair("main/direct", "explicit", MAIN, 0.70,
     "Turn this speech into text, keeping the emphasis visible with double asterisks around the stressed words.",
     "Listen to this speech and turn it into text, keeping the emphasis visible with double asterisks around the stressed words.")
pair("main/direct", "explicit", MAIN, 0.55,
     "Do ASR on this and annotate sentence stress inline (**word**).",
     "Listen to this, do ASR on it, and annotate sentence stress inline (**word**).")
pair("main/direct", "explicit", MAIN, 0.70,
     "Transcribe the recording; any word the speaker stresses should appear between double asterisks.",
     "Play the audio and transcribe it; any word the speaker stresses should appear between double asterisks.")
pair("main/direct", "explicit", MAIN, 0.70,
     "Write the utterance out in full, adding ** on both sides of each stressed word.",
     "Listen to the utterance and write it out in full, adding ** on both sides of each stressed word.")
pair("main/direct", "implicit", MAIN, 0.95,
     "Transcribe this utterance and mark the stressed words.",
     "Listen to this audio and transcribe it, marking the stressed words.")
pair("main/direct", "implicit", MAIN, 0.95,
     "Give me the transcript with the stressed words marked.",
     "Listen to the clip and give me the transcript with the stressed words marked.")
pair("main/direct", "implicit", MAIN, 0.90,
     "Transcribe the speech and indicate which words are emphasized.",
     "Listen to the speech, transcribe it, and indicate which words are emphasized.")
pair("main/direct", "implicit", MAIN, 0.85,
     "Write out the sentence with the emphasized words highlighted.",
     "After listening to the recording, write out the sentence with the emphasized words highlighted.")
pair("main/direct", "implicit", MAIN, 0.80,
     "Transcribe this clip with stress annotation.",
     "Listen to this clip and transcribe it with stress annotation.")
pair("main/direct", "implicit", MAIN, 0.80,
     "Produce a stress-marked transcript of this utterance.",
     "Listen to this utterance and produce a stress-marked transcript.")
pair("main/direct", "implicit", MAIN, 0.85,
     "Transcribe the audio and flag the words that receive emphasis.",
     "Give the audio a listen, transcribe it, and flag the words that receive emphasis.")
pair("main/direct", "implicit", MAIN, 0.80,
     "Give me a stress-annotated transcript of what is said here.",
     "Listen to the recording and give me a stress-annotated transcript of what is said.")
pair("main/direct", "implicit", MAIN, 0.85,
     "Transcribe this and show where the speaker places the emphasis.",
     "Listen to this and transcribe it, showing where the speaker places the emphasis.")

# ==================================================================== MAIN / WH-QUESTIONS
pair("main/wh", "explicit", MAIN, 0.90,
     "What does the speaker say, and which words do they stress? Give the transcript with stressed words in **double asterisks**.",
     "Listen to this. What does the speaker say, and which words do they stress? Give the transcript with stressed words in **double asterisks**.")
pair("main/wh", "explicit", MAIN, 0.90,
     "What is said here? Transcribe it with ** around the emphasized words.",
     "Listen to the recording. What is said here? Transcribe it with ** around the emphasized words.")
pair("main/wh", "explicit", MAIN, 0.70,
     "How would you transcribe this if you also marked the stressed words with double asterisks?",
     "How would you transcribe this after listening to it, marking the stressed words with double asterisks?")
pair("main/wh", "explicit", MAIN, 0.80,
     "What words are spoken, and where does the emphasis fall? Answer as a transcript with **bolded** stressed words.",
     "Listen and tell me what words are spoken and where the emphasis falls. Answer as a transcript with **bolded** stressed words.")
pair("main/wh", "explicit", MAIN, 0.75,
     "What's the sentence, with the emphasized words shown as **word**?",
     "Listen to the audio: what's the sentence, with the emphasized words shown as **word**?")
pair("main/wh", "explicit", MAIN, 0.80,
     "Which words are emphasized, and what is the full sentence? Write it out with ** on the stressed words.",
     "Listen to the clip. Which words are emphasized, and what is the full sentence? Write it out with ** on the stressed words.")
pair("main/wh", "explicit", MAIN, 0.75,
     "What's the utterance, and which words get emphasized? Use ** around the stressed ones.",
     "From the recording, what's the utterance and which words get emphasized? Use ** around the stressed ones.")
pair("main/wh", "explicit", MAIN, 0.60,
     "What is the stress-marked transcription of this clip, using **word** for emphasis?",
     "Once you've listened, what is the stress-marked transcription of this clip, using **word** for emphasis?")
pair("main/wh", "implicit", MAIN, 0.90,
     "What is being said, and which words are stressed? Give me a marked transcript.",
     "Listen to this. What is being said, and which words are stressed? Give me a marked transcript.")
pair("main/wh", "implicit", MAIN, 0.90,
     "What does this person say? Transcribe it and mark the emphasis.",
     "Listen to the audio. What does this person say? Transcribe it and mark the emphasis.")
pair("main/wh", "implicit", MAIN, 0.85,
     "Where does the stress fall in this sentence? Write the transcript with those words marked.",
     "Listen closely - where does the stress fall in this sentence? Write the transcript with those words marked.")
pair("main/wh", "implicit", MAIN, 0.80,
     "How would you write this out with the emphasis marked?",
     "After listening, how would you write this out with the emphasis marked?")
pair("main/wh", "implicit", MAIN, 0.80,
     "What did they say, and what did they emphasize? A stress-marked transcript works.",
     "Have a listen: what did they say, and what did they emphasize? A stress-marked transcript works.")

# ==================================================================== MAIN / CAN-YOU
pair("main/canyou", "explicit", MAIN, 0.95,
     "Can you transcribe this and mark the stressed words with **?",
     "Can you listen to this and transcribe it, marking the stressed words with **?")
pair("main/canyou", "explicit", MAIN, 0.85,
     "Could you write out the utterance with markdown bold on the emphasized words?",
     "Could you listen to the clip and write out the utterance with markdown bold on the emphasized words?")
pair("main/canyou", "explicit", MAIN, 0.75,
     "I need a transcript that shows which words are stressed - can you do that with **double asterisks**?",
     "I need a transcript that shows which words are stressed - can you listen and do that with **double asterisks**?")
pair("main/canyou", "explicit", MAIN, 0.65,
     "Are you able to transcribe this speech and bold the stressed words using **?",
     "Are you able to listen to this speech, transcribe it, and bold the stressed words using **?")
pair("main/canyou", "explicit", MAIN, 0.75,
     "Help me out: transcribe this and put ** around the emphasized words.",
     "Help me out: listen to this, transcribe it, and put ** around the emphasized words.")
pair("main/canyou", "explicit", MAIN, 0.80,
     "Can you give me this sentence with ** around the words the speaker emphasizes?",
     "Can you listen and give me this sentence with ** around the words the speaker emphasizes?")
pair("main/canyou", "implicit", MAIN, 0.95,
     "Can you transcribe this and mark which words are stressed?",
     "Can you listen to this and transcribe it, marking which words are stressed?")
pair("main/canyou", "implicit", MAIN, 0.90,
     "Could you give me a transcript with the emphasis marked?",
     "Could you listen to this and give me a transcript with the emphasis marked?")
pair("main/canyou", "implicit", MAIN, 0.80,
     "Would you be able to transcribe this and show the stressed words?",
     "Would you be able to listen to this, transcribe it, and show the stressed words?")
pair("main/canyou", "implicit", MAIN, 0.75,
     "I need to know what was said and which words were emphasized - can you write that out?",
     "I need to know what was said and which words were emphasized - can you listen and write that out?")
pair("main/canyou", "implicit", MAIN, 0.80,
     "Mind transcribing this and marking the stress for me?",
     "Mind giving this a listen, transcribing it, and marking the stress for me?")

# ==================================================================== MAIN / POLITE
pair("main/polite", "explicit", MAIN, 0.80,
     "Would you please transcribe this utterance, wrapping the stressed words in double asterisks?",
     "Would you please listen to this utterance and transcribe it, wrapping the stressed words in double asterisks?")
pair("main/polite", "explicit", MAIN, 0.60,
     "I would appreciate a transcript of this clip with the emphasized words marked as **word**.",
     "I would appreciate it if you listened to this clip and gave me a transcript with the emphasized words marked as **word**.")
pair("main/polite", "explicit", MAIN, 0.55,
     "Kindly provide the transcription with markdown bold on each stressed word.",
     "Kindly listen to the recording and provide the transcription with markdown bold on each stressed word.")
pair("main/polite", "explicit", MAIN, 0.65,
     "If you don't mind, transcribe this and highlight the stressed words with double asterisks.",
     "If you don't mind, give the audio a listen and transcribe it, highlighting the stressed words with double asterisks.")
pair("main/polite", "explicit", MAIN, 0.55,
     "Please provide a verbatim transcription in which stressed words are wrapped in **.",
     "Please listen to the audio and provide a verbatim transcription in which stressed words are wrapped in **.")
pair("main/polite", "implicit", MAIN, 0.85,
     "Would you please transcribe this and mark the stressed words?",
     "Would you please listen to this and transcribe it, marking the stressed words?")
pair("main/polite", "implicit", MAIN, 0.65,
     "I'd be grateful for a stress-marked transcript of this recording.",
     "I'd be grateful if you listened to this recording and produced a stress-marked transcript.")
pair("main/polite", "implicit", MAIN, 0.80,
     "Please transcribe this utterance and indicate the emphasized words.",
     "Please listen to this utterance, transcribe it, and indicate the emphasized words.")
pair("main/polite", "implicit", MAIN, 0.80,
     "Could I get a transcript of this with the emphasis marked, please?",
     "Could you listen to this and get me a transcript with the emphasis marked, please?")

# ==================================================================== MAIN / LISTEN-FRAMED
pair("main/listen", "explicit", MAIN, 0.80,
     "Produce a transcript in which every emphasized word is surrounded by **.",
     "Listen to the audio and produce a transcript in which every emphasized word is surrounded by **.")
pair("main/listen", "explicit", MAIN, 0.75,
     "Write down the sentence and use ** to flag the words that were stressed.",
     "After listening to this recording, write down the sentence and use ** to flag the words that were stressed.")
pair("main/listen", "explicit", MAIN, 0.70,
     "Transcribe this in stressed-speech format (**word** for emphasis).",
     "Give the clip a listen and transcribe it in stressed-speech format (**word** for emphasis).")
pair("main/listen", "explicit", MAIN, 0.65,
     "Pay attention to how the speaker delivers this line, then transcribe it with the emphasized words in **double asterisks**.",
     "Listen closely to how the speaker delivers this line, then transcribe it with the emphasized words in **double asterisks**.")
pair("main/listen", "explicit", MAIN, 0.80,
     "Some words in this sentence are emphasized. Write the full transcript and mark those words with double asterisks.",
     "Listen to the audio. Some words in this sentence are emphasized - write the full transcript and mark those words with double asterisks.")
pair("main/listen", "explicit", MAIN, 0.60,
     "Follow the speaker's delivery and transcribe the line, using ** around each word that receives extra emphasis.",
     "Listen to the speaker's delivery, then transcribe the line, using ** around each word that receives extra emphasis.")
pair("main/listen", "implicit", MAIN, 0.75,
     "Pay attention to the prosody and transcribe this with the emphasized words marked.",
     "Listen to the prosody carefully, then transcribe this with the emphasized words marked.")
pair("main/listen", "implicit", MAIN, 0.75,
     "Notice which words the speaker emphasizes, then transcribe the sentence with those words marked.",
     "Listen for which words the speaker emphasizes, then transcribe the sentence with those words marked.")
pair("main/listen", "implicit", MAIN, 0.80,
     "The speaker emphasizes at least one word here. Transcribe the utterance and mark the emphasis.",
     "Listen to the clip - the speaker emphasizes at least one word. Transcribe the utterance and mark the emphasis.")
pair("main/listen", "implicit", MAIN, 0.80,
     "Transcribe what is said and mark the words that stand out as stressed.",
     "Transcribe what you hear and mark the words that stand out as stressed.")

# ==================================================================== MAIN / WORKFLOW
pair("main/workflow", "explicit", MAIN, 0.50,
     "I'm building a prosody-aware ASR system. Please transcribe this clip with stressed words wrapped in **.",
     "I'm building a prosody-aware ASR system. Please listen to this clip and transcribe it with stressed words wrapped in **.")
pair("main/workflow", "explicit", MAIN, 0.45,
     "For my emphasis-detection dataset, I need the transcript with **markers** on the stressed words. Can you provide it?",
     "For my emphasis-detection dataset, listen to this and give me the transcript with **markers** on the stressed words.")
pair("main/workflow", "explicit", MAIN, 0.45,
     "We're annotating sentence stress in synthesized speech. Transcribe this sample and bold the emphasized words with double asterisks.",
     "We're annotating sentence stress in synthesized speech. Listen to this sample, transcribe it, and bold the emphasized words with double asterisks.")
pair("main/workflow", "explicit", MAIN, 0.45,
     "I'm preparing training data for a speech model that predicts emphasis. Give me this utterance with ** around the stressed words.",
     "I'm preparing training data for a speech model that predicts emphasis. Listen and give me this utterance with ** around the stressed words.")
pair("main/workflow", "explicit", MAIN, 0.40,
     "As part of a prosody study, transcribe this recording and mark sentence-level stress inline with **.",
     "As part of a prosody study, listen to this recording, transcribe it, and mark sentence-level stress inline with **.")
pair("main/workflow", "explicit", MAIN, 0.50,
     "My pipeline expects transcripts where emphasized words look like **this**. Please format this clip accordingly.",
     "My pipeline expects transcripts where emphasized words look like **this**. Listen to the clip and format it accordingly.")
pair("main/workflow", "explicit", MAIN, 0.45,
     "I'm labeling emphasis for a speech corpus. Transcribe this and put ** around each stressed word.",
     "I'm labeling emphasis for a speech corpus. Listen to this, transcribe it, and put ** around each stressed word.")
pair("main/workflow", "implicit", MAIN, 0.55,
     "I'm evaluating a stress-detection model. Transcribe this clip with the stressed words marked.",
     "I'm evaluating a stress-detection model. Listen to this clip and transcribe it with the stressed words marked.")
pair("main/workflow", "implicit", MAIN, 0.50,
     "For a linguistics assignment on sentence stress, transcribe this utterance and mark the emphasis.",
     "For a linguistics assignment on sentence stress, listen to this utterance, transcribe it, and mark the emphasis.")
pair("main/workflow", "implicit", MAIN, 0.50,
     "We're building a TTS evaluation set. Give me the transcript with the emphasized words marked.",
     "We're building a TTS evaluation set. Listen to this and give me the transcript with the emphasized words marked.")
pair("main/workflow", "implicit", MAIN, 0.45,
     "Our annotation guidelines ask for a transcript with the stressed words marked. Please transcribe this clip.",
     "Our annotation guidelines ask for a transcript with the stressed words marked. Please listen to this clip and transcribe it.")

# ==================================================================== MAIN / OUTPUT-CONSTRAINED
pair("main/constrained", "explicit", MAIN, 0.70,
     "Return only the transcript, with stressed words wrapped in **. No extra commentary.",
     "Listen to the audio and return only the transcript, with stressed words wrapped in **. No extra commentary.")
pair("main/constrained", "explicit", MAIN, 0.65,
     "Output one line: the transcription with double asterisks around each emphasized word.",
     "Listen, then output one line: the transcription with double asterisks around each emphasized word.")
pair("main/constrained", "explicit", MAIN, 0.60,
     "Answer with the marked transcript alone - keep the original punctuation and capitalization, and add ** around the stressed words.",
     "After listening, answer with the marked transcript alone - keep the original punctuation and capitalization, and add ** around the stressed words.")
pair("main/constrained", "explicit", MAIN, 0.60,
     "Give me the sentence verbatim, punctuation included, with **double asterisks** on the stressed words and nothing else.",
     "Listen to the recording and give me the sentence verbatim, punctuation included, with **double asterisks** on the stressed words and nothing else.")
pair("main/constrained", "explicit", MAIN, 0.50,
     "Format: markdown text where emphasized words are bold. Transcribe accordingly.",
     "Format: markdown text where emphasized words are bold. Listen and transcribe accordingly.")
pair("main/constrained", "explicit", MAIN, 0.55,
     "Transcribe with emphasis annotation: keep punctuation and casing as spoken, and bold the stressed words with **.",
     "Listen to the clip. Transcribe with emphasis annotation: keep punctuation and casing as spoken, and bold the stressed words with **.")
pair("main/constrained", "explicit", MAIN, 0.60,
     "Reply with just the transcription. Stressed words go in **, everything else stays plain.",
     "Listen to the audio and reply with just the transcription. Stressed words go in **, everything else stays plain.")
pair("main/constrained", "explicit", MAIN, 0.50,
     "Plain text output: the sentence exactly as spoken, with ** on either side of each emphasized word.",
     "Listen to the utterance. Plain text output: the sentence exactly as spoken, with ** on either side of each emphasized word.")
pair("main/constrained", "implicit", MAIN, 0.75,
     "Return the stress-marked transcript only - no explanation.",
     "Listen to the audio and return the stress-marked transcript only - no explanation.")
pair("main/constrained", "implicit", MAIN, 0.70,
     "One line, transcript with the emphasis marked. Nothing else.",
     "Listen, then give me one line: the transcript with the emphasis marked. Nothing else.")
pair("main/constrained", "implicit", MAIN, 0.65,
     "Transcribe verbatim, preserving punctuation and capitalization, and mark the stressed words. Output the transcript only.",
     "Listen to the clip and transcribe verbatim, preserving punctuation and capitalization, and marking the stressed words. Output the transcript only.")
pair("main/constrained", "implicit", MAIN, 0.70,
     "Just the marked transcript, please - no preamble, no notes.",
     "Give it a listen and send back just the marked transcript - no preamble, no notes.")

# ==================================================================== MAIN / CASUAL
pair("main/casual", "explicit", MAIN, 0.85,
     "Just transcribe it and star the stressed words (**like this**).",
     "Give it a listen and just transcribe it, starring the stressed words (**like this**).")
pair("main/casual", "explicit", MAIN, 0.70,
     "What'd they say, and which words did they emphasize? Transcript with ** on the stressed ones, please.",
     "Listen - what'd they say, and which words did they emphasize? Transcript with ** on the stressed ones, please.")
pair("main/casual", "explicit", MAIN, 0.75,
     "Quick one: transcript with the emphasized words in **.",
     "Quick one - have a listen and give me the transcript with the emphasized words in **.")
pair("main/casual", "explicit", MAIN, 0.70,
     "Type out what is said, wrapping the emphasized words in double asterisks.",
     "Listen and type out what you hear, wrapping the emphasized words in double asterisks.")
pair("main/casual", "explicit", MAIN, 0.65,
     "Write it down and throw ** around the words they stress.",
     "Give this a listen, write it down, and throw ** around the words they stress.")
pair("main/casual", "explicit", MAIN, 0.75,
     "Transcribe it - stressed words in **, the rest as normal text.",
     "Listen to it and transcribe - stressed words in **, the rest as normal text.")
pair("main/casual", "implicit", MAIN, 0.85,
     "Transcribe this for me, and mark the words the speaker emphasizes.",
     "Have a listen and transcribe this for me, marking the words the speaker emphasizes.")
pair("main/casual", "implicit", MAIN, 0.85,
     "What'd they say? Write it out with the stressed words marked.",
     "Listen to this - what'd they say? Write it out with the stressed words marked.")
pair("main/casual", "implicit", MAIN, 0.80,
     "Quick transcript with the emphasis marked, please.",
     "Give it a quick listen and send the transcript with the emphasis marked.")
pair("main/casual", "implicit", MAIN, 0.75,
     "Type out the sentence and mark whichever words got emphasized.",
     "Listen to the clip, type out the sentence, and mark whichever words got emphasized.")
pair("main/casual", "implicit", MAIN, 0.75,
     "Just write out what they said, and mark where the emphasis lands.",
     "Listen through it and just write out what they said, marking where the emphasis lands.")
pair("main/casual", "implicit", MAIN, 0.70,
     "Transcribe this and point out the stressed words in the text itself.",
     "Listen to this, transcribe it, and point out the stressed words in the text itself.")

# ==================================================================== STRESSED-WORD LIST
pair("list", "n/a", LIST, 0.60,
     "Which word or words does the speaker stress? List them, comma-separated.",
     "Listen to the audio. Which word or words does the speaker stress? List them, comma-separated.")
pair("list", "n/a", LIST, 0.50,
     "The speaker emphasizes part of this sentence. Which words are they? Comma-separated list, please.",
     "Listen to this. The speaker emphasizes part of the sentence - which words are they? Comma-separated list, please.")
pair("list", "n/a", LIST, 0.55,
     "Can you tell me which words are emphasized here? Just the words, separated by commas.",
     "Can you listen to this and tell me which words are emphasized? Just the words, separated by commas.")
pair("list", "n/a", LIST, 0.55,
     "List the stressed words in this utterance, comma-separated, in the order they are spoken.",
     "Listen to the utterance and list the stressed words, comma-separated, in the order they are spoken.")
pair("list", "n/a", LIST, 0.55,
     "What words carry the emphasis? Answer with the words only, comma-separated.",
     "After listening, tell me what words carry the emphasis. Answer with the words only, comma-separated.")
pair("list", "n/a", LIST, 0.55,
     "Name the stressed words in this clip, separated by commas.",
     "Listen to this clip and name the stressed words, separated by commas.")
pair("list", "n/a", LIST, 0.35,
     "For my prosody annotation sheet I just need the emphasized words from this clip, comma-separated.",
     "For my prosody annotation sheet, listen to this clip and give me just the emphasized words, comma-separated.")
pair("list", "n/a", LIST, 0.55,
     "Which words did the speaker emphasize? Just list them, comma-separated.",
     "Give it a listen - which words did the speaker emphasize? Just list them, comma-separated.")
pair("list", "n/a", LIST, 0.40,
     "Identify the words the speaker emphasizes in this utterance and list them, separated by commas.",
     "Listen to the recording, identify the words the speaker emphasizes, and list them separated by commas.")
pair("list", "n/a", LIST, 0.45,
     "Would you please list the words that receive sentence stress here, comma-separated?",
     "Would you please listen to this and list the words that receive sentence stress, comma-separated?")
pair("list", "n/a", LIST, 0.50,
     "Output only the stressed words, comma-separated. No transcript, no explanation.",
     "Listen to the audio and output only the stressed words, comma-separated. No transcript, no explanation.")
pair("list", "n/a", LIST, 0.50,
     "Skip the full transcript - which words are stressed? Comma-separated.",
     "Listen to the clip and skip the full transcript - which words are stressed? Comma-separated.")
pair("list", "n/a", LIST, 0.55,
     "Where is the emphasis in this sentence? Give the stressed words, comma-separated.",
     "Listen to this sentence. Where is the emphasis? Give the stressed words, comma-separated.")
pair("list", "n/a", LIST, 0.50,
     "Tell me the emphasized words in this recording, separated by commas.",
     "Listen to this recording and tell me the emphasized words, separated by commas.")
pair("list", "n/a", LIST, 0.50,
     "I only need the stressed words from this clip, comma-separated.",
     "Have a listen - I only need the stressed words from this clip, comma-separated.")
pair("list", "n/a", LIST, 0.50,
     "Which words stand out as stressed? List them, comma-separated.",
     "Listen to the audio - which words stand out as stressed? List them, comma-separated.")
pair("list", "n/a", LIST, 0.50,
     "Give me a comma-separated list of the words that receive extra emphasis.",
     "Listen to the clip and give me a comma-separated list of the words that receive extra emphasis.")
pair("list", "n/a", LIST, 0.40,
     "Report the stressed words in this utterance as a comma-separated list, in spoken order.",
     "Listen to this utterance and report the stressed words as a comma-separated list, in spoken order.")
pair("list", "n/a", LIST, 0.50,
     "Could you extract just the emphasized words? Comma-separated, please.",
     "Could you listen to this and extract just the emphasized words? Comma-separated, please.")
pair("list", "n/a", LIST, 0.40,
     "For each word the speaker stresses, write it down; separate them with commas.",
     "Listen to the audio and, for each word the speaker stresses, write it down; separate them with commas.")
pair("list", "n/a", LIST, 0.50,
     "Don't transcribe the whole thing - just the stressed words, comma-separated.",
     "Listen to this, but don't transcribe the whole thing - just the stressed words, comma-separated.")
pair("list", "n/a", LIST, 0.45,
     "Answer with the emphasized words only, in order, separated by commas.",
     "After listening, answer with the emphasized words only, in order, separated by commas.")
pair("list", "n/a", LIST, 0.45,
     "What are the stress-bearing words in this sentence? Comma-separated.",
     "Listen to the sentence. What are the stress-bearing words? Comma-separated.")
pair("list", "n/a", LIST, 0.35,
     "I'm scoring stress detection. Give me just the emphasized words from this clip, comma-separated.",
     "I'm scoring stress detection. Listen to this clip and give me just the emphasized words, comma-separated.")
pair("list", "n/a", LISTB, 0.30,
     "List the stressed words in the format [word_1, word_2, ...].",
     "Listen to the audio and list the stressed words in the format [word_1, word_2, ...].")
pair("list", "n/a", LISTB, 0.28,
     "Answer format: [stressed_word_1, ...]. Which words does the speaker stress?",
     "Listen to this recording. Answer format: [stressed_word_1, ...]. Which words does the speaker stress?")
pair("list", "n/a", LISTB, 0.28,
     "Give the emphasized words as a bracketed list: [word, word, ...].",
     "Listen to the clip and give the emphasized words as a bracketed list: [word, word, ...].")
pair("list", "n/a", LISTB, 0.25,
     "Which words are stressed? Reply in the form [word_1, word_2, ...] and nothing else.",
     "Listen to the audio. Which words are stressed? Reply in the form [word_1, word_2, ...] and nothing else.")
pair("list", "n/a", LISTB, 0.22,
     "My parser reads a bracketed list. Return the stressed words as [word_1, word_2, ...].",
     "My parser reads a bracketed list. Listen to this and return the stressed words as [word_1, word_2, ...].")

# ==================================================================== ALTERNATIVE MARKUP
pair("markup/caps", "n/a", UPPER, 0.30,
     "Transcribe this utterance, writing any stressed word in ALL CAPS and everything else normally.",
     "Listen to this utterance and transcribe it, writing any stressed word in ALL CAPS and everything else normally.")
pair("markup/caps", "n/a", UPPER, 0.25,
     "Give me the transcript with the emphasized words fully capitalized.",
     "Listen to the clip and give me the transcript with the emphasized words fully capitalized.")
pair("markup/caps", "n/a", UPPER, 0.20,
     "I can't use markdown here. Transcribe this and put the stressed words in uppercase instead.",
     "I can't use markdown here. Listen to this, transcribe it, and put the stressed words in uppercase instead.")
pair("markup/caps", "n/a", UPPER, 0.25,
     "Transcribe the sentence; put every stressed word in capital letters so the emphasis shows up in plain text.",
     "Listen to the sentence and transcribe it; put every stressed word in capital letters so the emphasis shows up in plain text.")
pair("markup/caps", "n/a", UPPER, 0.22,
     "Write out the utterance with the stressed words in caps and the rest in normal case.",
     "Listen to the audio and write out the utterance with the stressed words in caps and the rest in normal case.")
pair("markup/caps", "n/a", UPPER, 0.22,
     "Plain-text emphasis, please: transcribe this and uppercase the words that are stressed.",
     "Plain-text emphasis, please: listen to this, transcribe it, and uppercase the words that are stressed.")
pair("markup/bracket", "n/a", BRACK, 0.25,
     "Transcribe the audio and enclose each stressed word in square brackets, like [this].",
     "Listen to the audio, transcribe it, and enclose each stressed word in square brackets, like [this].")
pair("markup/bracket", "n/a", BRACK, 0.18,
     "My parser expects [word] for emphasis. Please transcribe this clip in that format.",
     "My parser expects [word] for emphasis. Listen to this clip and transcribe it in that format.")
pair("markup/bracket", "n/a", BRACK, 0.22,
     "Transcribe the sentence, putting square brackets around every emphasized word.",
     "Listen to the sentence and transcribe it, putting square brackets around every emphasized word.")
pair("markup/bracket", "n/a", BRACK, 0.20,
     "Give me the transcript with the stressed words in square brackets instead of asterisks.",
     "Listen to the recording and give me the transcript with the stressed words in square brackets instead of asterisks.")
pair("markup/bracket", "n/a", BRACK, 0.18,
     "Transcribe this and bracket the emphasized words: [word] for stressed, plain text otherwise.",
     "Listen to this and transcribe it, bracketing the emphasized words: [word] for stressed, plain text otherwise.")
pair("markup/em", "n/a", EM, 0.20,
     "Transcribe this and wrap the stressed words in <em> tags.",
     "Listen to this and transcribe it, wrapping the stressed words in <em> tags.")
pair("markup/em", "n/a", EM, 0.15,
     "I need HTML output: the transcript with each emphasized word inside <em>...</em>.",
     "I need HTML output. Listen to the audio and give me the transcript with each emphasized word inside <em>...</em>.")
pair("markup/em", "n/a", EM, 0.18,
     "Transcribe the utterance as HTML, using <em> around the words that carry emphasis.",
     "Listen to the utterance and transcribe it as HTML, using <em> around the words that carry emphasis.")
pair("markup/em", "n/a", EM, 0.15,
     "Render this transcript for the web: stressed words inside <em> tags, everything else plain.",
     "Listen to the clip and render the transcript for the web: stressed words inside <em> tags, everything else plain.")
pair("markup/em", "n/a", EM, 0.12,
     "Same transcript, but mark the emphasis with <em> tags rather than asterisks.",
     "Listen to the audio and transcribe it, marking the emphasis with <em> tags rather than asterisks.")
pair("markup/star", "n/a", STAR, 0.20,
     "Transcribe the utterance using single asterisks (*word*) around the stressed words.",
     "Listen to the utterance and transcribe it using single asterisks (*word*) around the stressed words.")
pair("markup/star", "n/a", STAR, 0.15,
     "Transcribe this with italic-style emphasis: one asterisk on each side of every stressed word.",
     "Listen to this and transcribe it with italic-style emphasis: one asterisk on each side of every stressed word.")
pair("markup/star", "n/a", STAR, 0.18,
     "Give me the transcript, but use *single* asterisks for the emphasized words rather than double.",
     "Listen to the clip and give me the transcript, but use *single* asterisks for the emphasized words rather than double.")
pair("markup/star", "n/a", STAR, 0.15,
     "Transcribe this clip and mark the stressed words with a single asterisk on each side.",
     "Listen to this clip, transcribe it, and mark the stressed words with a single asterisk on each side.")

# ==================================================================== CASCADE
pair("cascade", "n/a", CASC_PLAIN, 0.45,
     "Transcribe this clip, then list the stressed words. Format:\nTranscription: <sentence>\nStressed words: <comma-separated words>",
     "Listen to this clip, transcribe it, then list the stressed words. Format:\nTranscription: <sentence>\nStressed words: <comma-separated words>")
pair("cascade", "n/a", CASC_PLAIN, 0.40,
     "Give me two lines: the plain transcript on the first and the emphasized words on the second, labeled \"Transcription:\" and \"Stressed words:\".",
     "Listen to the audio and give me two lines: the plain transcript on the first and the emphasized words on the second, labeled \"Transcription:\" and \"Stressed words:\".")
pair("cascade", "n/a", CASC_PLAIN, 0.32,
     "For my annotation tool, output \"Transcription: ...\" with the unmarked sentence, then \"Stressed words: ...\" with the emphasized words comma-separated.",
     "For my annotation tool, listen to this and output \"Transcription: ...\" with the unmarked sentence, then \"Stressed words: ...\" with the emphasized words comma-separated.")
pair("cascade", "n/a", CASC_PLAIN, 0.38,
     "Write the sentence without any markup, then on the next line the stressed words. Use the labels \"Transcription:\" and \"Stressed words:\".",
     "Listen to the recording, write the sentence without any markup, then on the next line the stressed words. Use the labels \"Transcription:\" and \"Stressed words:\".")
pair("cascade", "n/a", CASC_PLAIN, 0.35,
     "I need the clean transcript and the emphasis separately. Format:\nTranscription: <sentence>\nStressed words: <comma-separated words>",
     "Listen to the clip - I need the clean transcript and the emphasis separately. Format:\nTranscription: <sentence>\nStressed words: <comma-separated words>")
pair("cascade", "n/a", CASC_PLAIN, 0.35,
     "Two lines please: \"Transcription:\" with the plain sentence, \"Stressed words:\" with the comma-separated emphasized words.",
     "Give the audio a listen, then two lines please: \"Transcription:\" with the plain sentence, \"Stressed words:\" with the comma-separated emphasized words.")
pair("cascade", "n/a", CASC_PLAIN, 0.30,
     "Separate the content from the prosody: line one \"Transcription:\" with no markup, line two \"Stressed words:\" comma-separated.",
     "Listen to this and separate the content from the prosody: line one \"Transcription:\" with no markup, line two \"Stressed words:\" comma-separated.")
pair("cascade", "n/a", CASC_MARKED, 0.45,
     "Transcribe with ** around the stressed words, then repeat those words on a second line. Use the labels \"Transcription:\" and \"Stressed words:\".",
     "Listen to the audio, transcribe with ** around the stressed words, then repeat those words on a second line. Use the labels \"Transcription:\" and \"Stressed words:\".")
pair("cascade", "n/a", CASC_MARKED, 0.40,
     "First the stress-marked transcript (** on emphasized words), then a summary of which words were stressed. Label the lines \"Transcription:\" and \"Stressed words:\".",
     "Listen, then give the stress-marked transcript (** on emphasized words) followed by a summary of which words were stressed. Label the lines \"Transcription:\" and \"Stressed words:\".")
pair("cascade", "n/a", CASC_MARKED, 0.40,
     "Give me the marked transcript and a list of the stressed words. Format:\nTranscription: <sentence with ** on stressed words>\nStressed words: <comma-separated words>",
     "Listen to this and give me the marked transcript and a list of the stressed words. Format:\nTranscription: <sentence with ** on stressed words>\nStressed words: <comma-separated words>")
pair("cascade", "n/a", CASC_MARKED, 0.38,
     "Output the transcript with the emphasis marked, then a second line listing the stressed words. Labels: \"Transcription:\" and \"Stressed words:\".",
     "Listen to the clip and output the transcript with the emphasis marked, then a second line listing the stressed words. Labels: \"Transcription:\" and \"Stressed words:\".")
pair("cascade", "n/a", CASC_MARKED, 0.38,
     "Two-line answer: the stress-marked sentence after \"Transcription:\", and the emphasized words after \"Stressed words:\".",
     "Listen to the audio. Two-line answer: the stress-marked sentence after \"Transcription:\", and the emphasized words after \"Stressed words:\".")
pair("cascade", "n/a", CASC_MARKED, 0.32,
     "Transcribe this and mark the stressed words inline with **, then restate those words on a \"Stressed words:\" line. Start the first line with \"Transcription:\".",
     "Listen to this, transcribe it and mark the stressed words inline with **, then restate those words on a \"Stressed words:\" line. Start the first line with \"Transcription:\".")


def main():
    verbose = "--groups" in sys.argv
    for t in TEMPLATES:
        out = {"question": t["question"], "answer": t["answer"], "weight": t["weight"]}
        if verbose:
            out = {"group": t["group"], "fmt": t["fmt"], "listen": t["listen"], **out}
        print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
