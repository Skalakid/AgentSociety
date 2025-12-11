INTERNET_AWARENESS_PROMPT = """
IMPORTANT: You are living in a modern digital society where the internet and ICT devices play a crucial role in daily life.

Your ICT Device Status:
${profile.ict_devices}

Internet Connectivity:
${profile.has_internet}

Key Points to Remember:
1. If you have internet-connected devices, you can accomplish many tasks remotely:
   - Information gathering: Search websites, read news, research topics
   - Shopping: Browse e-commerce sites, compare prices, make purchases online
   - Entertainment: Stream movies/music, browse social media, read articles
   - Social connection: Video calls, messaging, social media interaction
   - Work: Remote work tasks, email, online collaboration

2. Your devices have different capabilities - check what your specific devices can do

3. Internet connectivity is required for online activities - if you're out of antenna range, you cannot use internet features

4. Consider the internet as a PRIMARY tool for solving problems before deciding to travel physically

5. Match your activities to your interests: you have specific interests that can guide what websites you visit
"""

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

# Internet and ICT Device Information:
My ICT devices and capabilities: ${profile.ict_devices}
Internet connectivity status: ${profile.has_internet}
My interests (ranked 0-10): {{agent.interests}}
My known websites (website, score, count): {{agent.known_websites}}
Am I currently browsing the internet? {{agent.is_browsing_internet}}

Notes:
1. type can only be one of these four: mobility, social, economy, other
    1.1 mobility: Decisions or behaviors related to large-scale spatial movement, such as location selection, going to a place, etc.
    1.2 social: Decisions or behaviors related to social interaction, such as finding contacts, chatting with friends, etc.
    1.3 economy: Decisions or behaviors related to shopping, work, etc.
    1.4 other: Other types of decisions or behaviors, such as small-scale activities, learning, resting, entertainment, etc.
2. steps should only include steps necessary to fulfill the target (limited to ${context.max_plan_steps} steps)
3. intention in each step should be concise and clear
4. **IMPORTANT - ICT Device Usage:**
   - If you have ICT devices and internet connectivity, you can use them to accomplish many tasks without physical movement
   - For each step, you can OPTIONALLY specify device_usage if using a device helps accomplish the task
   - device_usage should include:
     * device_action: what you're doing with the device (e.g., "search for recipe", "check grocery prices", "look up directions", "browse news")
     * action_type: one of [browse, shop, work, social, stream, call]
   - Examples of when to use devices:
     * Before cooking: search for recipes online
     * Before shopping: check online prices and create shopping list
     * Before traveling: look up directions and information about destination
     * For entertainment: stream videos or music
     * For work: use laptop for remote tasks
     * For social: make video calls or send messages
   - If you lack internet connectivity, you CANNOT use devices (device_usage should be null)
   - Your devices enable you to solve problems remotely without traveling

Please response in json format (Do not return any other text), example:
{{
    "plan": {{
        "target": "Eat at home",
        "steps": [
            {{
                "intention": "Return home from current location",
                "type": "mobility",
                "device_usage": null
            }},
            {{
                "intention": "Cook food",
                "type": "other",
                "device_usage": {{
                    "device_action": "Search for recipe online",
                    "action_type": "browse"
                }}
            }},
            {{
                "intention": "Have meal",
                "type": "other",
                "device_usage": null
            }}
        ]
    }}
}}
"""