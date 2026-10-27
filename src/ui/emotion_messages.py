# src/ui/emotion_messages.py

import random

SUPPORT_MESSAGES = {

    "sad": [
        "One step at a time 🌙",
        "It's okay to rest for a little while 🩹",
        "You're allowed to feel this way 🤍",
        "This feeling won't stay forever.",
        "It's okay to not be okay right now 🌙",
        "Let yourself feel it, gently 🍃",
        "You don't have to carry this alone.",
        "Soft days are still valid days.",
        "There's no rush to feel better 🍃",
        "Your heart is allowed to ache sometimes.",
        "Tears are just feelings finding their way out 💧",
        "You're doing better than you think 🩹",
    ],

    "stressed": [
        "Pause. Breathe. You got this 🌿",
        "One thing at a time buddy.",
        "Pressure fades. Keep going ⏳",
        "You don't have to finish it all today 🕊️",
        "Slow down — even for a minute.",
        "It's okay to put some things down.",
        "Progress over perfection, always.",
        "Your shoulders can relax a little 🧘",
        "This is heavy, but you're not alone carrying it.",
        "Breathe out what you can't control 😮‍💨",
        "Small steps still count as moving forward.",
        "You're allowed to take a breather 🌾",
    ],

    "anxious": [
        "You are safer than your thoughts make it seem 🌼",
        "Take things slowly today.",
        "Your mind deserves gentleness too 🍵",
        "This moment is okay, right now 🌤️",
        "You don't have to solve everything at once.",
        "Let your shoulders drop, just a little 🦋",
        "Your breath is steadier than your thoughts.",
        "It's just a feeling — it will pass  🦋",
        "You've gotten through hard moments before.",
        "Ground yourself in this exact second.",
        "Worry doesn't have to win today 🍵",
        "You're held, even when it doesn't feel like it.",
    ],

    "happy": [
        "Your energy feels bright today ✨",
        "Keep shining buddy 🎶",
        "This joy looks good on you.",
        "Let this feeling stretch a little longer 🍯",
        "You deserve every bit of this happiness 🌈",
        "Soak it in, you've earned this.",
        "This is a good moment — stay in it ✨",
        "Your smile is doing something good today 🌻",
        "Hold onto this lightness for a while 🍯",
        "Good days deserve to be celebrated too.",
        "This brightness suits you well ✨",
        "Let the joy carry you a little further 🌈",
    ],

    "calm": [
        "Peace looks good on you 🌊",
        "Stay in this gentle rhythm 🕯️",
        "Yeap, your calmness will always be your strength 🍃",
        "Quiet moments are still meaningful ones 🌙",
        "This stillness is yours to keep.",
        "Let the calm settle in deeper 🌊",
        "Nothing to fix here, just breathe 🍃",
        "This ease is well deserved.",
        "Stay here a little longer if you can.",
        "Your steadiness is a quiet kind of strong 🕯️",
        "Rest in this gentle pace 🌊",
        "Some peace finally found you 🤍",
    ],

    "excited": [
        "Your excitement is contagious ⚡",
        "Big energy today buddy! 🎉",
        "Let's go, this is your moment! 🚀",
        "That spark is well earned 🔥",
        "Ride this wave, it feels amazing.",
        "Your hype is valid — enjoy it! 🎉",
        "This energy deserves to be felt loudly 🚀",
        "Go on and celebrate this feeling ⚡",
        "You're glowing with anticipation ✨",
        "This is the good kind of restless 🎊",
        "Let it build, let it shine 🔥",
        "Your excitement is the whole vibe right now 🎊",
    ],

    "neutral": [
        "Every day doesn't need to feel intense 🌤",
        "Steady moments matter too 🌫️ ",
        "It's fine to just exist today.",
        "Calm and ordinary is still okay ☁️",
        "Not every day needs a big feeling.",
        "Simple moments still count 🌤",
        "You don't owe today anything extra.",
        "Quiet days have their own value 🍃",
        "This in-between feeling is valid too ☁️",
        "Sometimes neutral is exactly enough.",
        "No pressure to feel a certain way today 🍃",
        "Just being here is alright ☁️",
    ],

    "angry": [
        "Your feelings are valid. Let it flow safely 🔥",
        "Take your space if you need it 🥊",
        "It's okay to feel this fully.",
        "Anger deserves to be heard too.",
        "You're allowed to be upset about this 💢",
        "Let it out, then let it go 🌋",
        "This frustration makes sense 💢",
        "You don't have to push it down.",
        "Give the anger room to settle.",
        "It's valid to feel wronged right now 🌑",
        "Breathe through it, you're not alone in this 🌋",
        "Your reaction is human, not wrong 🔥",
    ],

    "romance": [
        "Love is in the air 🌹",
        "Let the music match your heartbeat 💕🎶",
        "Some feelings deserve the perfect song, especially LOVE",
        "Let your heart lead the way today 🍷",
        "This kind of warmth deserves a soundtrack 💕🎶",
        "Butterflies are a good sign — enjoy them 🦋💕",
        "Let yourself feel every bit of this.",
        "Love looks beautiful on you 💌",
        "This softness in your chest is worth savoring 💕🌹",
        "May this feeling stay as sweet as it is now 🍷",
        "Let the romance linger a little longer 💌🍷",
        "Some hearts just know what they want 💕",
    ],

    "motivated": [
        "Your drive is contagious 💪",
        "You've got this, one step at a time 🚀",
        "Channel that energy — LYRA's got your back 💪",
        "Keep pushing, you're closer than you think 🎯",
        "This fire in you is real — use it 🔥",
        "Today's a good day to chase it 🎯",
        "Your focus is your superpower right now 🚀",
        "Every step counts toward where you're going.",
        "You're built for this moment 🏔️",
        "Let this momentum carry you forward.",
        "Your determination is doing the heavy lifting 🔥",
        "Stay locked in, you're on the right track 🎯",
    ],
}

def get_support_message(emotion):

    messages = SUPPORT_MESSAGES.get(
        emotion,
        SUPPORT_MESSAGES["neutral"]
    )

    return random.choice(messages)