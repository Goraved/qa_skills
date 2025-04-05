"""Skill related functionality"""
from typing import List, Dict, Any

from data import query
from common_utils import get_all_by_table

class Skill:
    """Skill container class"""
    def __init__(self, skill_id: int = None, name: str = None):
        self.id = skill_id
        self.name = name

def get_skills() -> Dict[str, int]:
    """Get all skills as a dictionary with zero counts"""
    skills = get_all_by_table('skills')
    return {name: 0 for name in skills}

def get_skills_info() -> List[Dict[str, Any]]:
    """Get all skills with their IDs"""
    skills = []
    rows = query('SELECT id, name FROM skills ORDER BY name')
    for row in rows:
        skills.append({'id': row[0], 'name': row[1]})
    return skills

# Alias for backward compatibility
get_skill_list = get_skills_info