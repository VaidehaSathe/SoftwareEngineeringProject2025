import pandas as pd

BookDataframe = {
    "title": [
        "The Clockmaker’s Paradox",
        "Whispers Beneath the Willow",
        "Echoes of the Forgotten Sea",
        "The Cartographer’s Daughter",
        "A Symphony for the Stars"
    ],
    "description": [
        "In a small, fog-covered town, a reclusive clockmaker discovers a pocket watch that seems to run backward. When he winds it, fragments of time begin to unravel, revealing lost moments and forgotten tragedies. As the watch’s power grows, he learns it is bound to a mysterious traveler who vanished decades earlier. Each tick threatens to erase parts of reality, forcing him to confront his past and the consequences of tampering with time. 'The Clockmaker’s Paradox' blends historical fiction with magical realism, exploring themes of regret, memory, and the fragile balance between invention and destiny.",

        "Beneath the shadow of an ancient willow tree, a young woman uncovers letters buried by her grandmother during the war. The letters tell of secret meetings, forbidden love, and acts of quiet rebellion against oppression. As she pieces together the story, she begins to realize how deeply her family’s history intertwines with the village’s silent wounds. Torn between uncovering the truth and protecting those still haunted by it, she must decide whether to let the past rest or bring it to light. 'Whispers Beneath the Willow' is a poignant exploration of memory, silence, and redemption.",

        "On a forgotten island lost to maps, a young sailor washes ashore after a violent storm. The sea, it seems, remembers him, whispering secrets through the tide. Guided by a cryptic journal and an aging lighthouse keeper, he begins to uncover the fate of a vanished expedition. As he ventures deeper into the island’s ruins, reality starts to dissolve, and the line between myth and memory blurs. 'Echoes of the Forgotten Sea' is a lyrical tale of loss, discovery, and the haunting persistence of the ocean’s call.",

        "When an ambitious young woman inherits her father’s collection of unfinished maps, she is drawn into a mystery that spans continents. Each map holds clues to a journey he never completed and a secret he never shared. Determined to finish what he began, she follows his faded trails through deserts, mountains, and forgotten cities. Along the way, she discovers that maps are not only guides to places but to the people we lose. 'The Cartographer’s Daughter' is a sweeping adventure about legacy, belonging, and the courage to navigate one’s own path.",

        "Set in a distant future where music is forbidden, a gifted composer hides her melodies among the stars. Each constellation hums with fragments of her symphony, echoing across galaxies. When a young astronomer decodes the cosmic harmonies, he becomes the unlikely guardian of her legacy. Together, they must evade those who fear the return of art’s power and reignite the world’s lost music. 'A Symphony for the Stars' is a luminous story of resistance, creation, and the timeless bond between art and the human spirit."
    ]
}

df = pd.DataFrame(BookDataframe)
df.to_csv('data/preprocessor_mock-data/books_mock_data.csv', index=False)
