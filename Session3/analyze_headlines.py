"""
GNews Data Analysis
Reads headlines from CSV and answers all 8 analytical questions.
"""

import os
import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple
from pathlib import Path


class HeadlinesAnalyzer:
    def __init__(self, csv_file: str = 'headlines.csv'):
        self.csv_file = csv_file
        self.headlines = []
        self.load_data()
    
    def load_data(self):
        """Load all headlines from CSV."""
        if not os.path.exists(self.csv_file):
            print(f"[ERROR] {self.csv_file} not found")
            return False
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.headlines = list(reader)
            print(f"[OK] Loaded {len(self.headlines)} headlines from {self.csv_file}\n")
            return True
        except Exception as e:
            print(f"[ERROR] Error loading CSV: {e}")
            return False
    
    def question_1_most_headlines(self) -> str:
        """Q1: Which country published the most headlines today?"""
        country_counts = defaultdict(int)
        
        for headline in self.headlines:
            country = headline.get('country', 'N/A')
            country_counts[country] += 1
        
        if not country_counts:
            return "No data available"
        
        max_country, max_count = max(country_counts.items(), key=lambda item: item[1])
        
        result = f"{max_country} published the most headlines with {max_count} headlines\n\n"
        result += "Breakdown by country:\n"
        for country in sorted(country_counts.keys()):
            result += f"  {country}: {country_counts[country]}\n"
        
        return result
    
    def question_2_avg_words_per_country(self) -> str:
        """Q2: What is the average number of words in a headline title — per country?"""
        country_stats = defaultdict(lambda: {'total_words': 0, 'count': 0})
        
        for headline in self.headlines:
            title = headline.get('title', 'N/A')
            if title and title != 'N/A':
                word_count = len(title.split())
                country = headline.get('country', 'N/A')
                country_stats[country]['total_words'] += word_count
                country_stats[country]['count'] += 1
        
        result = "Average number of words per headline title by country:\n"
        for country in sorted(country_stats.keys()):
            stats = country_stats[country]
            if stats['count'] > 0:
                avg_words = stats['total_words'] / stats['count']
                result += f"  {country}: {avg_words:.2f} words (total: {stats['total_words']}, count: {stats['count']})\n"
        
        return result
    
    def question_3_duplicate_headlines(self) -> str:
        """Q3: Are there any headlines that appeared in more than one country? If yes, which ones?"""
        title_countries = defaultdict(list)
        
        for headline in self.headlines:
            title = headline.get('title', 'N/A').lower().strip()
            country = headline.get('country', 'N/A')
            if title and title != 'n/a':
                title_countries[title].append(country)
        
        # Find titles that appear in multiple countries
        duplicates = {title: countries for title, countries in title_countries.items() 
                     if len(set(countries)) > 1}
        
        if not duplicates:
            result = "No headlines appeared in more than one country.\n"
        else:
            result = f"Found {len(duplicates)} headline(s) that appeared in multiple countries:\n\n"
            for title, countries in sorted(duplicates.items()):
                unique_countries = list(set(countries))
                result += f"  Countries: {', '.join(unique_countries)}\n"
                result += f"  Title: {title}\n\n"
        
        return result
    
    def question_4_most_prolific_source(self) -> str:
        """Q4: Which news source published the most headlines across all 5 countries combined?"""
        source_counts = defaultdict(int)
        
        for headline in self.headlines:
            source = headline.get('source', 'N/A')
            if source and source != 'N/A':
                source_counts[source] += 1
        
        if not source_counts:
            return "No source data available"
        
        # Get top 5 sources
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        
        result = f"Most prolific news source: {sorted_sources[0][0]} with {sorted_sources[0][1]} headlines\n\n"
        result += "Top 10 sources:\n"
        for i, (source, count) in enumerate(sorted_sources[:10], 1):
            result += f"  {i}. {source}: {count} headlines\n"
        
        return result
    
    def question_5_publication_time_split(self) -> str:
        """Q5: What percentage of all headlines were published in the last 6 hours vs older than 6 hours?"""

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=6)

        recent_count = 0
        older_count = 0
        unparseable = 0

        for headline in self.headlines:
            published_at = headline.get("published_at")

            if not published_at:
                unparseable += 1
                continue

            try:
                # Normalize ISO format (handles Z properly)
                pub_time = datetime.fromisoformat(
                    published_at.replace("Z", "+00:00")
                )

                # Ensure UTC comparison
                if pub_time.tzinfo is None:
                    pub_time = pub_time.replace(tzinfo=timezone.utc)
                else:
                    pub_time = pub_time.astimezone(timezone.utc)

                if pub_time >= cutoff:
                    recent_count += 1
                else:
                    older_count += 1

            except Exception:
                unparseable += 1

        total = recent_count + older_count

        if total == 0:
            return "No valid publication times to analyze"

        recent_pct = (recent_count / total) * 100
        older_pct = (older_count / total) * 100

        result = (
            "Publication time distribution:\n"
            f"  Last 6 hours: {recent_count} ({recent_pct:.1f}%)\n"
            f"  Older than 6 hours: {older_count} ({older_pct:.1f}%)\n"
            f"  Unparseable timestamps: {unparseable}\n"
        )

        return result
    
    def question_6_duplicate_prevention(self) -> str:
        """Q6: If you run your script twice, does your database end up with duplicate rows? How did you prevent that?"""
        result = """Duplicate Prevention Strategy:

            1. Headline Hash Generation:
            - Each headline is hashed using MD5(title + source)
            - This creates a unique identifier for each unique headline+source combination
            - Identical headlines from the same source are detected

            2. Before Adding New Headlines:
            - The script reads all existing headline_hash values from CSV
            - Stores them in a set for O(1) lookup performance
            - Any new article with a hash already in the set is skipped

            3. Implementation Details:
            - Function: generate_headline_hash() creates MD5 hash of "title|source"
            - Function: get_existing_headlines_hashes() loads all hashes from CSV
            - Before inserting, headline_hash is checked against existing hashes
            - The 'headline_hash' column in CSV enables deduplication across runs

            4. Result:
            - Running the script multiple times WILL NOT create duplicate rows
            - Only genuinely new headlines are added each time
            - The CSV grows with new content, not duplicates

            Example:
            Run 1: Fetches 30 headlines → CSV has 30 rows
            Run 2: Fetches 30 headlines (10 new, 20 same) → CSV has 40 rows (only 10 new added)
            """
        return result
    
    def question_7_long_headlines_filter(self) -> str:
        """Q7: Save only headlines with a title longer than 6 words to a CSV. How many passed that filter?"""
        filtered_headlines = []
        
        for headline in self.headlines:
            title = headline.get('title', 'N/A')
            if title and title != 'N/A':
                word_count = len(title.split())
                if word_count > 6:
                    filtered_headlines.append(headline)
        
        # Save to filtered CSV
        output_file = 'headlines_long_titles.csv'
        if filtered_headlines:
            try:
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['country', 'title', 'description', 'url', 'image', 'source', 
                                'published_at', 'article_content', 'headline_hash']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(filtered_headlines)
                
                result = f"{len(filtered_headlines)} headlines with title > 6 words saved to {output_file}\n\n"
            except Exception as e:
                result = f"Error saving filtered headlines: {e}\n\n"
        else:
            result = "No headlines found with title > 6 words\n\n"
        
        # Show statistics
        result += "Word count distribution:\n"
        word_counts = defaultdict(int)
        for headline in self.headlines:
            title = headline.get('title', 'N/A')
            if title and title != 'N/A':
                word_count = len(title.split())
                word_counts[word_count] += 1
        
        for words in sorted(word_counts.keys()):
            count = word_counts[words]
            status = "[FILTERED]" if words > 6 else ""
            result += f"  {words} words: {count} headlines {status}\n"
        
        return result
    
    def question_8_longest_shortest_headlines(self) -> str:
        """Q8: Which country had the longest headline on average — and which had the shortest?"""
        country_words = defaultdict(list)
        
        for headline in self.headlines:
            title = headline.get('title', 'N/A')
            country = headline.get('country', 'N/A')
            if title and title != 'N/A':
                word_count = len(title.split())
                country_words[country].append(word_count)
        
        if not country_words:
            return "No headline data available"
        
        # Calculate averages
        country_avgs = {}
        for country, words_list in country_words.items():
            if words_list:
                avg = sum(words_list) / len(words_list)
                country_avgs[country] = avg
        
        if not country_avgs:
            return "No data to analyze"
        
        longest_country = max(country_avgs.items(), key=lambda item: item[1])[0]
        shortest_country = min(country_avgs.items(), key=lambda item: item[1])[0]
        
        result = f"Headline length by country (average words):\n\n"
        result += f"Longest average: {longest_country} with {country_avgs[longest_country]:.2f} words\n"
        result += f"Shortest average: {shortest_country} with {country_avgs[shortest_country]:.2f} words\n\n"
        
        result += "All countries ranked:\n"
        for country, avg in sorted(country_avgs.items(), key=lambda x: x[1], reverse=True):
            result += f"  {country}: {avg:.2f} words\n"
        
        return result
    
    def run_all_analyses(self, output_file: str = 'analysis_results.txt') -> bool:
        """
        Run all 8 analyses and save results to a text file.
        
        Args:
            output_file: Name of the output text file (default: analysis_results.txt)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.headlines:
            print("[ERROR] No data to analyze. Run gnews_pipeline.py first.")
            return False
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Write header
                f.write("=" * 70 + "\n")
                f.write("GNews Headlines Analysis - All 8 Questions\n")
                f.write("=" * 70 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                
                questions = [
                    ("Q1: Most headlines by country?", self.question_1_most_headlines),
                    ("Q2: Average words per headline by country?", self.question_2_avg_words_per_country),
                    ("Q3: Headlines in multiple countries?", self.question_3_duplicate_headlines),
                    ("Q4: Most prolific news source?", self.question_4_most_prolific_source),
                    ("Q5: Publication time distribution (last 6 hours)?", self.question_5_publication_time_split),
                    ("Q6: Duplicate prevention strategy?", self.question_6_duplicate_prevention),
                    ("Q7: Long headlines (>6 words) filter?", self.question_7_long_headlines_filter),
                    ("Q8: Longest vs shortest headline by country?", self.question_8_longest_shortest_headlines),
                ]
                
                # Write each question and its result
                for question_title, question_func in questions:
                    f.write(f"\n{question_title}\n")
                    f.write("-" * 70 + "\n")
                    result = question_func()
                    f.write(result)
                    f.write("\n")
                
                # Write footer
                f.write("=" * 70 + "\n")
                f.write("Analysis Complete\n")
                f.write("=" * 70 + "\n")
            
            # Console output summary
            print("[OK] Analysis saved to analysis_results.txt")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save analysis: {e}")
            return False


def main():
    analyzer = HeadlinesAnalyzer('headlines.csv')
    analyzer.run_all_analyses()


if __name__ == "__main__":
    main()
