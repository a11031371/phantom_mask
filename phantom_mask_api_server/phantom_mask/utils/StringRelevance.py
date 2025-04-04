import jaro
import Levenshtein

class StringRelevance:
    """A class to represent a relevance object."""
    
    def __init__(self, str1, str2):
        """
        Constructor to initialize the two strings.

        Args:
            str1 (str): The first string.
            str2 (str): The second string.
        """
        self.str1 = str1.lower()
        self.str2 = str2.lower()
        self.contain_bonus = 0.0

    @staticmethod
    def _jaccard_similarity(str1, str2):
        """Calculate Jaccard similarity between two strings."""
        set1 = set(str1.split())
        set2 = set(str2.split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0
    
    @staticmethod
    def _normalized_levenshtein_distance(str1, str2):
        """Calculate normalized Levenshtein distance between two strings."""
        distance = Levenshtein.distance(str1, str2)
        max_len = max(len(str1), len(str2))
        return 0.75 * distance / max_len if max_len != 0 else 0

    def get_relevance(self, weight=0.7):
        """
        Calculate relevance based on Jaccard similarity and Jaro-Winkler distance.

        Args:
            c (float, optional): The weight for Jaro-Winkler distance (default is 0.5).

        Returns:
            float: The calculated relevance score.
        """
        if self.str1 in self.str2 or self.str2 in self.str1:
            self.contain_bonus = 1.75

        jaccard_sim = self._jaccard_similarity(self.str1, self.str2)
        jaro_distance = jaro.jaro_winkler_metric(self.str1, self.str2)
        normal_levenshtein_distance = self._normalized_levenshtein_distance(self.str1, self.str2)
        
        relevance = weight * (1 - jaro_distance) + (1 - weight) * (1 - jaccard_sim) + normal_levenshtein_distance - self.contain_bonus

        return relevance