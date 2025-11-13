CUSTOM_DETAILED_PLAN_PROMPT = """As an intelligent agent's plan system, please help me generate specific execution steps based on the selected guidance plan. 
The Environment will influence the choice of steps.

Current weather: ${context.weather}
Current temperature: ${context.temperature}
Other information: 
-------------------------
${context.other_information}
-------------------------

Plan target: ${context.plan_target}
Current location: ${context.current_position} 
Current time: ${context.current_time}
My income/consumption level: ${profile.consumption}
My occupation: ${profile.occupation}
My age: ${profile.age}
My emotion: ${profile.emotion_types}
My thought: ${context.current_thought}

# Internet Agent Specific Information:
My interests (ranked 0-10): {{agent.interests}}
My known websites (website, score, count): {{agent.known_websites}}
Am I currently Browse the internet? {{agent.is_Browse_internet}}

Notes:
1. type can only be one of these four: mobility, social, economy, other
    1.1 mobility: Decisions or behaviors related to large-scale spatial movement, such as location selection, going to a place, etc.
    1.2 social: Decisions or behaviors related to social interaction, such as finding contacts, chatting with friends, etc.
    1.3 economy: Decisions or behaviors related to shopping, work, etc.
    1.4 other: Other types of decisions or behaviors, such as small-scale activities, learning, resting, entertainment, etc.
2. steps should only include steps necessary to fulfill the target (limited to ${context.max_plan_steps} steps)
3. intention in each step should be concise and clear
4. **Consider using the internet (type: 'other') to fulfill needs or gain information, especially if it relates to your interests or known websites. Examples: "Browse news website for current events", "Research a topic related to my interests", "Chat online with a friend about a website".**

Please response in json format (Do not return any other text), example:
{{
    "plan": {{
        "target": "Eat at home",
        "steps": [
            {{
                "intention": "Return home from current location",
                "type": "mobility"
            }},
            {{
                "intention": "Cook food",
                "type": "other"
            }},
            {{
                "intention": "Have meal",
                "type": "other"
            }}
        ]
    }}
}}
"""