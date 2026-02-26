"""
OHDSI Athena API Integration

Fetches concept information from OHDSI Athena vocabulary service.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

import requests
from typing import Dict, List, Optional
import time


class AthenaAPI:
    """Client for OHDSI Athena vocabulary API"""

    BASE_URL = "https://athena.ohdsi.org/api/v1"

    @staticmethod
    def get_concept_info(concept_id: int, retries: int = 3) -> Optional[Dict]:
        """
        Fetch concept information from Athena

        Args:
            concept_id: OMOP concept ID
            retries: Number of retry attempts

        Returns:
            Dict with concept info or None if not found
        """
        url = f"{AthenaAPI.BASE_URL}/concepts/{concept_id}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://athena.ohdsi.org/',
            'Origin': 'https://athena.ohdsi.org'
        }

        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'concept_id': concept_id,
                        'concept_name': data.get('name'),
                        'domain_id': data.get('domainId'),
                        'vocabulary_id': data.get('vocabularyId'),
                        'concept_class_id': data.get('conceptClassId'),
                        'standard_concept': data.get('standardConcept'),
                        'concept_code': data.get('conceptCode'),
                        'valid_start_date': data.get('validStartDate'),
                        'valid_end_date': data.get('validEndDate'),
                        'invalid_reason': data.get('invalidReason')
                    }
                elif response.status_code == 404:
                    return None
                else:
                    if attempt < retries - 1:
                        time.sleep(1)
                        continue
                    return None
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                print(f"Error fetching concept {concept_id}: {e}")
                return None

        return None

    @staticmethod
    def get_concepts_batch(concept_ids: List[int]) -> Dict[int, Dict]:
        """
        Fetch multiple concepts with rate limiting

        Args:
            concept_ids: List of concept IDs

        Returns:
            Dict mapping concept_id -> concept info
        """
        results = {}

        for concept_id in concept_ids:
            info = AthenaAPI.get_concept_info(concept_id)
            if info:
                results[concept_id] = info
            time.sleep(0.5)

        return results

    @staticmethod
    def get_related_concepts(concept_id: int, relationship_type: str = "all") -> List[Dict]:
        """
        Fetch related concepts from Athena

        Args:
            concept_id: OMOP concept ID
            relationship_type: Type of relationship (e.g., 'Subsumes', 'Maps to', 'all')

        Returns:
            List of related concept dicts
        """
        url = f"{AthenaAPI.BASE_URL}/concepts/{concept_id}/related"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://athena.ohdsi.org/'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                related = []
                for item in data:
                    related.append({
                        'concept_id': item.get('CONCEPT_ID_2'),
                        'concept_name': item.get('CONCEPT_NAME'),
                        'relationship': item.get('RELATIONSHIP_ID'),
                        'domain': item.get('DOMAIN_ID'),
                        'vocabulary': item.get('VOCABULARY_ID')
                    })
                return related[:20]
        except Exception as e:
            print(f"Error fetching related concepts for {concept_id}: {e}")
            return []

        return []

    @staticmethod
    def enrich_concept_set(concept_ids: List[int]) -> List[Dict]:
        """
        Enrich concept IDs with names and metadata from Athena

        Args:
            concept_ids: List of OMOP concept IDs

        Returns:
            List of dicts with concept details
        """
        print(f"Fetching concept names from OHDSI Athena for {len(concept_ids)} concepts...")

        enriched = []
        for concept_id in concept_ids:
            info = AthenaAPI.get_concept_info(concept_id)
            if info:
                enriched.append(info)
                print(f"  ✓ {concept_id}: {info['concept_name']}")
            else:
                enriched.append({
                    'concept_id': concept_id,
                    'concept_name': f'Concept {concept_id}',
                    'domain_id': 'Unknown',
                    'vocabulary_id': 'Unknown'
                })
                print(f"  ⚠ {concept_id}: Not found in Athena")

        return enriched
