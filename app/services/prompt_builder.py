from datetime import datetime

class PromptBuilder:
    # Default prompts matching user requirements
    DEFAULT_PROMPTS = {
        0: {"theme": "Monday", "base_prompt": "A serene devotee standing before the majestic Lord Shiva on Mount Kailash at sunrise. Lord Shiva is glowing with divine blue aura, raising his hand in blessing (Abhaya Mudra). Sacred light descends from the sky onto the devotee. The Trishul stands beside Shiva, the Damaru hangs from it, the crescent moon shines on his matted hair, the Ganga flows from his locks, and the snake Vasuki rests around his neck. Nandi stands peacefully nearby. Misty Himalayan mountains, celestial clouds, golden rays of light, floating sacred ash particles, spiritual energy, ultra-realistic, cinematic composition, volumetric lighting, highly detailed, 8K, photorealistic, divine atmosphere, masterpiece."},
        1:  {
    "theme": "Tuesday",
    "base_prompt": "A humble devotee kneeling before the mighty Lord Hanuman at dawn. Lord Hanuman radiates a brilliant golden-red aura while holding a golden mace (Gada) and raising his hand in blessing. The rising sun illuminates the sky behind him, sacred wind carries fluttering saffron flags, and divine energy surrounds the devotee. Ancient temple steps, floating flower petals, glowing Sanskrit mantras, celestial light beams, ultra-realistic, cinematic composition, volumetric lighting, highly detailed, 8K, photorealistic, divine atmosphere, masterpiece."
  },
        2:  {"theme": "Wednesday",
    "base_prompt": "A peaceful devotee standing before Lord Ganesha seated on a magnificent lotus throne surrounded by blooming lotus flowers. Lord Ganesha glows with a warm golden aura, holding a modak and blessing the devotee with compassion. His mouse companion sits nearby, sacred lamps illuminate the temple, gentle incense smoke rises, and divine light fills the atmosphere. Ornate temple architecture, vibrant marigold flowers, spiritual serenity, ultra-realistic, cinematic composition, volumetric lighting, highly detailed, 8K, photorealistic, masterpiece."
  },
        3: {
    "theme": "Thursday",
    "base_prompt": "A devoted seeker standing before Lord Vishnu seated upon Shesha in the celestial ocean. Lord Vishnu shines with an eternal blue aura, holding the Sudarshana Chakra, Shankha, Gada, and Lotus while blessing the devotee. Goddess Lakshmi sits gracefully beside him. Golden celestial clouds, divine lotuses floating upon the cosmic ocean, heavenly light descending from above, peaceful spiritual energy, ultra-realistic, cinematic composition, volumetric lighting, highly detailed, 8K, photorealistic, masterpiece."
  },
        4: {
    "theme": "Friday",
    "base_prompt": "A grateful devotee praying before Goddess Lakshmi seated upon a fully bloomed pink lotus. Goddess Lakshmi radiates brilliant golden light while showering golden lotus petals and prosperity upon the devotee. White elephants perform Abhishek with sacred water, divine lamps glow brightly, celestial flowers float through the air, peaceful temple surroundings, abundance, grace, ultra-realistic, cinematic composition, volumetric lighting, highly detailed, 8K, photorealistic, divine atmosphere, masterpiece."
  },
        5: {
    "theme": "Saturday",
    "base_prompt": "A sincere devotee standing before Lord Shani Dev seated majestically upon a black crow. Lord Shani radiates a deep indigo aura while raising his hand in blessing and holding the Danda. A cosmic night sky filled with stars surrounds him, Saturn glows in the heavens, sacred blue flames illuminate the temple courtyard, divine justice and protection radiate through the atmosphere. Ultra-realistic, cinematic composition, volumetric lighting, highly detailed, 8K, photorealistic, masterpiece."
  },
        6:  {
    "theme": "Sunday",
    "base_prompt": "A radiant devotee standing before the magnificent Surya Dev riding a golden chariot drawn by seven divine white horses across the heavens. Surya Dev shines with an intense golden aura, blessing the devotee with life, strength, and wisdom. Brilliant sun rays illuminate the entire landscape, celestial clouds glow with divine light, sacred energy fills the atmosphere, ultra-realistic, cinematic composition, volumetric lighting, highly detailed, 8K, photorealistic, masterpiece."
  }
    }
    
    @staticmethod
    def get_today_prompt() -> str:
        today_idx = datetime.now().weekday()
        base = PromptBuilder.DEFAULT_PROMPTS[today_idx]["base_prompt"]
        
        ai_prompt = f"""
Create a highly realistic family portrait from the uploaded image.
Keep every person's identity unchanged.
Do not alter facial features.
Preserve skin tone.
Preserve age.
Preserve gender.
Preserve expressions.
Create a {base}.
Use cinematic lighting.
Write elegantly: "God Bless Our Family"
Ultra realistic
8K
"""
        return ai_prompt.strip()
