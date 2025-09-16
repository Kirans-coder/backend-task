import os
import openai

def score_leads(leads, offer):
    """
    Runs the full scoring pipeline (Rule-based + AI) for a list of leads.
    """
    scored_leads = []
    for lead in leads:
        # Rule Layer
        rule_score = calculate_rule_score(lead, offer)
        
        # AI Layer
        ai_intent, ai_reasoning = get_ai_score(lead, offer)
        ai_points = {"High": 50, "Medium": 30, "Low": 10}.get(ai_intent, 0)
        
        # Final Score & Label
        final_score = rule_score + ai_points
        final_intent = ai_intent
        
        scored_leads.append({
            "name": lead.get("name", ""),
            "role": lead.get("role", ""),
            "company": lead.get("company", ""),
            "intent": final_intent,
            "score": final_score,
            "reasoning": ai_reasoning
        })
    return scored_leads

def calculate_rule_score(lead, offer):
    """Calculates the rule-based score for a single lead."""
    score = 0
    
    # 1. Role Relevance (+20, +10, 0)
    decision_makers = ["Head", "Director", "Founder", "VP", "Chief"]
    influencers = ["Manager", "Specialist", "Lead"]
    
    role = lead.get("role", "")
    if any(title in role for title in decision_makers):
        score += 20
    elif any(title in role for title in influencers):
        score += 10
        
    # 2. Industry Match (+20, +10, 0)
    ideal_industries = [case.lower() for case in offer["ideal_use_cases"]]
    industry = lead.get("industry", "").lower()
    
    if industry in ideal_industries:
        score += 20
    # Example of an "adjacent" industry check
    elif "tech" in industry and "saas" in " ".join(ideal_industries):
        score += 10
        
    # 3. Data Completeness (+10)
    required_fields = ["name", "role", "company", "industry", "location", "linkedin_bio"]
    if all(lead.get(field) for field in required_fields):
        score += 10
        
    return score

def get_ai_score(lead, offer):
    """Uses OpenAI to get a classification and reasoning."""
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Prompt Engineering
    prompt = f"""
    Product Offer:
    Name: {offer['name']}
    Value Props: {', '.join(offer['value_props'])}
    Ideal Use Cases: {', '.join(offer['ideal_use_cases'])}

    Prospect Profile:
    Name: {lead['name']}
    Role: {lead['role']}
    Company: {lead['company']}
    Industry: {lead['industry']}
    Location: {lead['location']}
    LinkedIn Bio: {lead['linkedin_bio']}

    Task: Classify this prospect's buying intent as 'High', 'Medium', or 'Low' and explain your reasoning in 1-2 sentences.
    Output format: Intent: <label>, Reasoning: <text>
    """
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003", # Or another suitable model
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        # Parse the AI response
        response_text = response.choices[0].text.strip()
        parts = response_text.split(", Reasoning: ")
        intent = parts[0].replace("Intent: ", "").strip()
        reasoning = parts[1].strip() if len(parts) > 1 else "No reasoning provided."
        
        # Ensure the intent is one of the valid labels
        if intent not in ["High", "Medium", "Low"]:
            intent = "Low" # Default to Low if AI output is unexpected
        
        return intent, reasoning
    except Exception as e:
        print(f"AI call failed: {e}")
        return "Low", "Failed to get AI score due to an API error."