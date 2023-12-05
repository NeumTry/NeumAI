from typing import List
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
        raise NotImplementedError("In the works. Contact founders@tryneum.com for information")