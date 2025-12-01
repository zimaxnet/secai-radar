"""
Example: Using Model Layer in Orchestrator

This demonstrates how the orchestrator layer uses the Model Layer
according to the blueprint architecture.
"""

from models import get_model_layer


async def example_orchestration_workflow():
    """
    Example orchestration workflow that uses the Model Layer.
    
    This follows the blueprint's orchestration pattern:
    1. Plan which tools to call
    2. Call collectors
    3. Normalize to silver
    4. Ask the model to summarize per domain
    5. Assemble report sections
    """
    
    # Initialize Model Layer
    model_layer = get_model_layer()
    
    # Step 1: Plan which tools to call (using reasoning model)
    planning_prompt = """
    Analyze the assessment scope and determine which collectors should be called.
    Scope: Network security and identity management domains.
    """
    
    planning_result = await model_layer.reasoning(
        prompt=planning_prompt,
        context={
            "scope": ["network", "identity"],
            "available_collectors": ["nsg_collector", "rbac_collector"],
        }
    )
    
    print("Planning result:", planning_result["content"])
    
    # Step 2: Call collectors (simulated - actual implementation calls collectors)
    # This would be done by the collectors module
    collected_evidence = [
        {"resource_type": "nsg", "resource_id": "nsg-001", "rules": [...]},
        {"resource_type": "rbac", "resource_id": "rbac-001", "assignments": [...]},
    ]
    
    # Step 3: Normalize to silver (using classification model)
    normalized_controls = []
    
    for evidence in collected_evidence:
        # Classify evidence to control/domain
        classification = await model_layer.classify(evidence)
        
        if classification["classification"]:
            normalized_controls.append({
                "evidence": evidence,
                "control_id": classification["classification"]["control_id"],
                "domain_code": classification["classification"]["domain_code"],
                "confidence": classification["classification"]["confidence_score"],
            })
    
    # Step 4: Ask the model to summarize per domain (using reasoning model)
    domain_summaries = {}
    
    for control in normalized_controls:
        domain = control["domain_code"]
        
        if domain not in domain_summaries:
            domain_summaries[domain] = []
        
        domain_summaries[domain].append(control)
    
    # Generate summaries for each domain
    summaries = {}
    for domain, controls in domain_summaries.items():
        summary_prompt = f"""
        Summarize the security posture for the {domain} domain based on the following controls.
        Provide key findings, strengths, and gaps.
        """
        
        summary_result = await model_layer.reasoning(
            prompt=summary_prompt,
            context={"controls": controls},
        )
        
        summaries[domain] = summary_result["content"]
    
    # Step 5: Assemble report sections (using generation model)
    # Generate executive summary
    executive_summary = await model_layer.generate(
        section_type="executive_summary",
        data={
            "overall_score": 75,
            "domains": summaries,
            "key_findings": ["finding1", "finding2"],
        },
    )
    
    # Generate findings section
    findings_section = await model_layer.generate(
        section_type="findings_by_domain",
        data={
            "domains": summaries,
            "controls": normalized_controls,
        },
    )
    
    # Generate recommendations
    recommendations = await model_layer.generate(
        section_type="recommendations",
        data={
            "gaps": ["gap1", "gap2"],
            "priorities": ["high", "medium"],
        },
    )
    
    # Assemble final report
    report = {
        "executive_summary": executive_summary["content"],
        "findings": findings_section["content"],
        "recommendations": recommendations["content"],
        "metadata": {
            "model_usage": {
                "reasoning_calls": 2,
                "classification_calls": len(collected_evidence),
                "generation_calls": 3,
            },
        },
    }
    
    return report


async def example_self_review_workflow():
    """
    Example of iterative self-review workflow as mentioned in the blueprint.
    
    The orchestrator can use the reasoning model to review its own outputs
    and iterate for improvement.
    """
    
    model_layer = get_model_layer()
    
    # Initial generation
    initial_content = await model_layer.generate(
        section_type="findings",
        data={"controls": [...]},
    )
    
    # Self-review: Ask the model to review its own output
    review_prompt = f"""
    Review the following security assessment findings for accuracy, completeness, and clarity.
    Provide feedback and suggest improvements.
    
    Findings:
    {initial_content["content"]}
    """
    
    review_result = await model_layer.reasoning(
        prompt=review_prompt,
        context={"original_content": initial_content["content"]},
    )
    
    # Refine based on review
    refined_content = await model_layer.generate(
        section_type="findings",
        data={
            "controls": [...],
            "review_feedback": review_result["content"],
        },
    )
    
    return refined_content


if __name__ == "__main__":
    import asyncio
    
    # Run example workflow
    result = asyncio.run(example_orchestration_workflow())
    print("Report generated:", result)

