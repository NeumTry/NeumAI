from typing import List
from scipy.spatial.distance import cosine
from pydantic import BaseModel, Field
from neumai.Pipelines.Pipeline import Pipeline
from neumai.Shared.NeumSearch import NeumSearchResult

class PipelineCollection(BaseModel):
    """
    Pipeline Collection

    Collections of Pipelines that can be managed as a unit. Includes running and searching them as a unit.

    Attributes
    ----------

    pipelines : List[Pipeline]
        List of Neum AI Pipelines
    
    """
    
    pipelines: List[Pipeline] = Field(..., description = "Pipelines that are to be par of the collection.")

    def run(self):
        for pipeline in self.pipelines:
            pipeline.run()
    
    def search_unified(self, query:str, number_of_results:int) -> List[NeumSearchResult]:
        """Search pipelines and unify results using scores as re-ranking criteria"""
        
        # Simple query of results
        search_results = []
        for pipeline in self.pipelines:
            results = pipeline.search(query=query, number_of_results=number_of_results)
            search_results.append(results)

        # Re-rank results by score. Should add a callback option for re-rank
        return sorted(search_results, key=lambda x: x.score, reverse=True)[:number_of_results]

    def search_separate(self, query:str, number_of_results:int)-> List:
        """Search pipelines and provide raw results for each pipeline"""
        
        # Simple query of results
        search_results = []
        for pipeline in self.pipelines:
            results = pipeline.search(query=query, number_of_results=number_of_results)
            search_results.append({
                "pipeline_id":pipeline.id,
                "results" : results
            })

        # Re-rank results by score. Should add a callback option for re-rank
        return (search_results)
    
    def search_routed(self, query:str, number_of_results:int)-> List:
        """Routed search based on the contents available in a pipeline"""
        # Need to add descriptions to the pipeline and generate a basic index on top of them

        pipe_to_similarity = {}
        for pipe in self.pipelines:
            pipe_representative = pipe.sink.get_representative_vector()
            query_vector = pipe.embed.embed_query(query=query)
            distance_from_representative = cosine(pipe_representative, query_vector)

            # Similarity score, hence subtracted distance from 1
            pipe_to_similarity[pipe.id] = 1 - distance_from_representative

        # We want to sort by decreasing oeder of similarity score
        # The more similar the query to a given representative vector
        # the higher rank that pipeline would get in terms of search.
        # Currently, we are only selection the only pipeline whose 
        # representative is most similar to the query.
        pipe_to_similarity = dict(sorted(pipe_to_similarity.items(), key=lambda x: x[1], reverse=True)[:1])

        search_results = []
        for pipe_id,similarity_score in pipe_to_similarity.items():
            for pipe in self.pipelines:
                if pipe.id==pipe_id:
                    results = pipe.search(query=query, number_of_results=number_of_results)
                    break
        search_results.append(results)
        return search_results
        # raise NotImplementedError("In the works. Contact founders@tryneum.com for information")