"""
Script to fetch all topics from the database with their names and prerequisites.
This will be used to include topic information in the AI prompt.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Import repository
from backend.app import create_app
from flask import Flask

# Create app context
app = create_app()

with app.app_context():
    repo = app.extensions.get("repository")
    
    if not repo:
        print("ERROR: Repository not initialized")
        sys.exit(1)
    
    # Get all topics
    print("Fetching all topics from database...")
    topics = repo.get_topics()
    
    print(f"\nFound {len(topics)} topics\n")
    print("=" * 80)
    print("ALL TOPICS WITH PREREQUISITES")
    print("=" * 80)
    print()
    
    # Format topics for prompt inclusion
    topics_list = []
    for topic in topics:
        topic_id = topic.get("id", "N/A")
        name = topic.get("name", "Unknown")
        description = topic.get("description", "")
        jamb_weight = topic.get("jamb_weight", 0.0)
        prerequisite_ids = topic.get("prerequisite_topic_ids", [])
        subject = topic.get("subject", "Mathematics")
        
        # prerequisite_topics is a text[] array containing topic names directly (not IDs)
        prerequisite_topics = topic.get("prerequisite_topics", [])
        if not isinstance(prerequisite_topics, list):
            prerequisite_topics = []
        
        topics_list.append({
            "id": topic_id,
            "name": name,
            "description": description,
            "subject": subject,
            "jamb_weight": jamb_weight,
            "prerequisite_topics": prerequisite_topics  # text[] array of topic names
        })
        
        # Print formatted topic
        print(f"Topic: {name}")
        print(f"  ID: {topic_id}")
        print(f"  Subject: {subject}")
        if description:
            print(f"  Description: {description}")
        if jamb_weight:
            print(f"  JAMB Weight: {jamb_weight * 100:.1f}%")
        if prerequisite_topics:
            print(f"  Prerequisites: {', '.join(prerequisite_topics)}")
        else:
            print(f"  Prerequisites: None")
        print()
    
    print("=" * 80)
    print("FORMATTED FOR PROMPT INCLUSION")
    print("=" * 80)
    print()
    print("Available Topics and Prerequisites:")
    print()
    for topic in topics_list:
        prereq_text = f" (Prerequisites: {', '.join(topic['prerequisite_topics'])})" if topic.get('prerequisite_topics') else " (No prerequisites)"
        print(f"- {topic['name']}{prereq_text}")
    
    print()
    print("=" * 80)
    print("JSON FORMAT (for programmatic use)")
    print("=" * 80)
    print()
    import json
    print(json.dumps(topics_list, indent=2))
    
    # Save to file
    with open("all_topics.json", "w", encoding="utf-8") as f:
        json.dump(topics_list, f, indent=2)
    
    print()
    print(f"[OK] Topics saved to: all_topics.json")
    print(f"[OK] Total topics: {len(topics_list)}")

