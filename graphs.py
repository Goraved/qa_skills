import os
import logging
from datetime import date
from typing import List, Tuple

# Configure matplotlib to use a non-interactive backend to avoid thread issues
import matplotlib

matplotlib.use('Agg')  # Use Agg backend - important to set this before importing pyplot
import matplotlib.pyplot as plt
from flask import abort

from models.position import get_positions_statistics_by_date
from models.skill import get_skills_info
from models.statistic import get_statistics_by_skill, get_statistics_by_date, Statistic
from models.vacancy import get_vacancies_statistics_by_date
from models.way import get_ways_statistics_by_date

# Configure logging
logger = logging.getLogger(__name__)

# Global matplotlib instance
PLT = plt


def get_stats(date_collected: date) -> Tuple:
    """Get statistics for a specific date"""
    if not os.path.isfile('./static/images/languages.png'):
        try:
            get_languages_comparison()
        except Exception as e:
            logger.error(f"Error generating language comparison: {e}")
            # Continue even if language comparison fails

    try:
        # Get all statistics - using direct function calls instead of asyncio
        links = get_vacancies_statistics_by_date(date_collected)
        positions = get_positions_statistics_by_date(date_collected)
        ways = get_ways_statistics_by_date(date_collected)
        stats = get_statistics_by_date(date_collected)

        # Generate tech info
        tech = [{'vac_count': len(links), 'date_collected': stats[0].date_collected if stats else date_collected}]

        return links, stats, positions, ways, tech
    except Exception as e:
        logger.error(f"Error getting stats for date {date_collected}: {e}")
        raise


def get_skill_stats(skill_id: int) -> Tuple:
    """Get statistics for a specific skill"""
    try:
        # Get skill stats - using direct function calls
        stats = get_statistics_by_skill(skill_id)
        skills = get_skills_info()

        # Find selected skill
        selected_skill = [skill for skill in skills if skill['id'] == skill_id]
        if not selected_skill:
            abort(400, f'Unknown skill_id - "{skill_id}"')

        # Generate graph
        save_graph(stats, selected_skill[0]["name"])

        return stats, skills, selected_skill
    except Exception as e:
        logger.error(f"Error getting skill stats for skill_id {skill_id}: {e}")
        raise


def save_graph(stats: List[Statistic], name: str, title='graph'):
    """Save a graph for a specific skill"""
    try:
        # Make sure output directory exists
        os.makedirs('static/images', exist_ok=True)

        # Create a new figure for each graph or reuse the current one if possible
        try:
            # Try to access current axes, create new figure if not available
            if not plt.get_fignums():
                plt.figure()
        except Exception:
            # If there's an issue, create a fresh figure
            plt.figure()

        # Check if this skill is already plotted
        legend_texts = []
        if plt.gca().get_legend():
            legend_texts = [text._text for text in plt.gca().get_legend().texts]

        if not legend_texts or name not in legend_texts:
            # Prepare data
            count_skill = [stat.count for stat in stats][::-1]
            date_collected = [stat.date_collected for stat in stats][::-1]

            # Plot data
            plt.plot(date_collected, count_skill, label=name)
            plt.title(title)
            plt.legend(loc="upper left")
            plt.ylabel('Skill matched in vacancies')
            plt.xlabel('Date collected')
            plt.xticks(rotation=90)

            # Save figure - ensure tight layout before saving
            plt.tight_layout()
            plt.savefig(f'static/images/{title}.png')
            logger.info(f"Graph saved for {name} as {title}.png")
    except Exception as e:
        logger.error(f"Error saving graph for {name}: {e}")
        # Continue without raising to avoid breaking the application


def get_languages_comparison():
    """Generate language comparison graph"""
    # Make sure output directory exists
    os.makedirs('static/images', exist_ok=True)

    try:
        # Clear any existing plot
        clear_plt()

        # Create a single figure for all languages
        plt.figure(figsize=(10, 6))

        # Get skills info once to reuse
        skills = get_skills_info()
        skill_dict = {skill['id']: skill['name'] for skill in skills}

        # Plot each language skill
        for skill_id in (6, 7, 10, 11, 46):
            try:
                # Skip if skill not found
                if skill_id not in skill_dict:
                    logger.warning(f"Skill with ID {skill_id} not found, skipping")
                    continue

                # Get statistics for this skill
                stats = get_statistics_by_skill(skill_id)
                if not stats:
                    logger.warning(f"No statistics found for skill ID {skill_id}, skipping")
                    continue

                # Prepare data
                skill_name = skill_dict[skill_id]
                count_skill = [stat.count for stat in stats][::-1]
                date_collected = [stat.date_collected for stat in stats][::-1]

                # Plot data
                plt.plot(date_collected, count_skill, label=skill_name)

            except Exception as e:
                logger.error(f"Error processing language skill {skill_id}: {e}")
                # Continue with other skills

        # Set plot properties for all data
        plt.title('Language Comparison')
        plt.legend(loc="upper left")
        plt.ylabel('Skill matched in vacancies')
        plt.xlabel('Date collected')
        plt.xticks(rotation=90)
        plt.tight_layout()

        # Save figure
        plt.savefig('static/images/languages.png')
        logger.info("Language comparison graph generated")

        # Crop the image to remove extra whitespace
        try:
            from PIL import Image
            img = Image.open('static/images/languages.png')
            width, height = img.size
            img.crop((0, 50, width, height)).save('static/images/languages.png')
            logger.info("Language comparison graph cropped")
        except Exception as e:
            logger.error(f"Error cropping language comparison image: {e}")

        # Clear plot for future use
        clear_plt()

    except Exception as e:
        logger.error(f"Error generating language comparison: {e}")
        # Create an empty placeholder file if graph generation fails
        if not os.path.exists('static/images/languages.png'):
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, 'Graph generation failed',
                     horizontalalignment='center', verticalalignment='center')
            plt.savefig('static/images/languages.png')
            plt.close()


def clear_plt():
    """Clear matplotlib plot"""
    # Close all existing figures to free up memory
    plt.close('all')

    # We'll create a new figure only when needed, not here
    # This prevents creating GUI elements in non-main threads