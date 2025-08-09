"""Discovery agent for requirements gathering and project analysis."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from .base_agent import BaseAgent, AgentCapability, AgentState, TaskResult
from .agent_memory import MemoryType


class DiscoveryAgent(BaseAgent):
    """
    Discovery agent specialized in requirements gathering, stakeholder analysis,
    and project scope definition.
    
    Capabilities:
    - Requirements elicitation and analysis
    - Stakeholder identification and mapping
    - Project scope definition
    - Risk identification
    - Constraint analysis
    - Success criteria definition
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """Initialize the discovery agent."""
        super().__init__(
            agent_id=agent_id,
            name="Discovery Agent",
            agent_type="discovery",
            config=config,
            capabilities=[
                AgentCapability.REQUIREMENTS_ANALYSIS,
                AgentCapability.RESEARCH,
                AgentCapability.COMMUNICATION
            ],
            description="Specialized agent for requirements gathering and project discovery"
        )
        
        # Discovery-specific configuration
        self.max_stakeholders = config.get("max_stakeholders", 20)
        self.requirement_categories = config.get("requirement_categories", [
            "functional", "non_functional", "business", "technical", "regulatory"
        ])
        self.analysis_depth = config.get("analysis_depth", "detailed")
    
    async def _execute_task_impl(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Execute discovery-specific tasks."""
        task_type = task_data.get("type", "unknown")
        
        try:
            if task_type == "requirements_gathering":
                return await self._gather_requirements(task_data, context)
            elif task_type == "stakeholder_analysis":
                return await self._analyze_stakeholders(task_data, context)
            elif task_type == "scope_definition":
                return await self._define_scope(task_data, context)
            elif task_type == "risk_identification":
                return await self._identify_risks(task_data, context)
            elif task_type == "constraint_analysis":
                return await self._analyze_constraints(task_data, context)
            elif task_type == "success_criteria":
                return await self._define_success_criteria(task_data, context)
            else:
                return TaskResult(
                    success=False,
                    error=f"Unknown discovery task type: {task_type}"
                )
        
        except Exception as e:
            self.logger.error(f"Discovery task execution failed: {str(e)}")
            return TaskResult(
                success=False,
                error=f"Discovery task execution failed: {str(e)}"
            )
    
    async def _gather_requirements(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Gather and analyze project requirements."""
        self.logger.info("Starting requirements gathering")
        
        project_description = task_data.get("project_description", "")
        stakeholder_input = task_data.get("stakeholder_input", [])
        existing_docs = task_data.get("existing_documentation", [])
        
        # Analyze project description
        requirements = await self._analyze_project_description(project_description)
        
        # Process stakeholder input
        if stakeholder_input:
            stakeholder_requirements = await self._process_stakeholder_input(stakeholder_input)
            requirements.extend(stakeholder_requirements)
        
        # Analyze existing documentation
        if existing_docs:
            doc_requirements = await self._extract_requirements_from_docs(existing_docs)
            requirements.extend(doc_requirements)
        
        # Categorize and prioritize requirements
        categorized_requirements = await self._categorize_requirements(requirements)
        prioritized_requirements = await self._prioritize_requirements(categorized_requirements)
        
        # Store in memory
        await self.memory.store_context(
            context_type="requirements_gathering",
            content={
                "requirements": prioritized_requirements,
                "categories": list(categorized_requirements.keys()),
                "total_count": len(requirements),
                "project_description": project_description
            },
            memory_type=MemoryType.LONG_TERM,
            importance=0.9
        )
        
        return TaskResult(
            success=True,
            result={
                "requirements": prioritized_requirements,
                "summary": {
                    "total_requirements": len(requirements),
                    "categories": list(categorized_requirements.keys()),
                    "high_priority_count": len([r for r in requirements if r.get("priority") == "high"])
                }
            },
            metadata={"task_type": "requirements_gathering"}
        )
    
    async def _analyze_project_description(self, description: str) -> List[Dict[str, Any]]:
        """Extract requirements from project description using AI."""
        if not description:
            return []
        
        prompt = f"""
        Analyze the following project description and extract specific requirements:
        
        Project Description:
        {description}
        
        Please identify:
        1. Functional requirements (what the system should do)
        2. Non-functional requirements (performance, security, usability)
        3. Business requirements (goals, constraints, success criteria)
        4. Technical requirements (platforms, technologies, integrations)
        
        Format each requirement as a clear, testable statement.
        """
        
        try:
            response = await self.generate_response(prompt)
            requirements = await self._parse_requirements_response(response)
            return requirements
        except Exception as e:
            self.logger.error(f"Failed to analyze project description: {str(e)}")
            return []
    
    async def _process_stakeholder_input(self, stakeholder_input: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process input from various stakeholders."""
        requirements = []
        
        for input_item in stakeholder_input:
            stakeholder_role = input_item.get("role", "unknown")
            input_text = input_item.get("input", "")
            priority = input_item.get("priority", "medium")
            
            if input_text:
                stakeholder_requirements = await self._extract_stakeholder_requirements(
                    input_text, stakeholder_role, priority
                )
                requirements.extend(stakeholder_requirements)
        
        return requirements
    
    async def _extract_stakeholder_requirements(
        self,
        input_text: str,
        role: str,
        priority: str
    ) -> List[Dict[str, Any]]:
        """Extract requirements from individual stakeholder input."""
        prompt = f"""
        Extract specific requirements from the following stakeholder input:
        
        Stakeholder Role: {role}
        Input: {input_text}
        
        Consider the stakeholder's perspective and expertise when interpreting their input.
        Extract clear, actionable requirements that reflect their needs and concerns.
        """
        
        try:
            response = await self.generate_response(prompt)
            requirements = await self._parse_requirements_response(response)
            
            # Add stakeholder context
            for req in requirements:
                req["stakeholder_role"] = role
                req["stakeholder_priority"] = priority
            
            return requirements
        except Exception as e:
            self.logger.error(f"Failed to extract stakeholder requirements: {str(e)}")
            return []
    
    async def _extract_requirements_from_docs(self, docs: List[str]) -> List[Dict[str, Any]]:
        """Extract requirements from existing documentation."""
        requirements = []
        
        for doc in docs:
            doc_requirements = await self._analyze_document_for_requirements(doc)
            requirements.extend(doc_requirements)
        
        return requirements
    
    async def _analyze_document_for_requirements(self, document: str) -> List[Dict[str, Any]]:
        """Analyze a single document for requirements."""
        prompt = f"""
        Analyze the following document and extract any explicit or implicit requirements:
        
        Document:
        {document[:2000]}...  # Truncate for token limits
        
        Look for:
        - Stated requirements or specifications
        - Implied functionality from descriptions
        - Constraints or limitations mentioned
        - Success criteria or acceptance conditions
        """
        
        try:
            response = await self.generate_response(prompt)
            requirements = await self._parse_requirements_response(response)
            
            for req in requirements:
                req["source"] = "documentation"
            
            return requirements
        except Exception as e:
            self.logger.error(f"Failed to analyze document: {str(e)}")
            return []
    
    async def _categorize_requirements(self, requirements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize requirements by type."""
        categorized = {category: [] for category in self.requirement_categories}
        
        for req in requirements:
            category = req.get("category", "functional")
            if category in categorized:
                categorized[category].append(req)
            else:
                categorized["functional"].append(req)
        
        return categorized
    
    async def _prioritize_requirements(self, categorized_requirements: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Prioritize requirements within each category."""
        prioritized = {}
        
        for category, requirements in categorized_requirements.items():
            # Sort by priority (high, medium, low)
            priority_order = {"high": 3, "medium": 2, "low": 1}
            sorted_requirements = sorted(
                requirements,
                key=lambda x: priority_order.get(x.get("priority", "medium"), 2),
                reverse=True
            )
            prioritized[category] = sorted_requirements
        
        return prioritized
    
    async def _parse_requirements_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured requirements."""
        # This is a simplified parser - in practice, you'd want more sophisticated parsing
        requirements = []
        
        lines = response.split('\n')
        current_requirement = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-', '*')):
                if current_requirement:
                    requirements.append(current_requirement)
                
                current_requirement = {
                    "id": f"REQ-{len(requirements) + 1:03d}",
                    "description": line,
                    "category": "functional",
                    "priority": "medium",
                    "status": "identified",
                    "created_at": datetime.utcnow().isoformat()
                }
            elif current_requirement and line:
                current_requirement["description"] += " " + line
        
        if current_requirement:
            requirements.append(current_requirement)
        
        return requirements
    
    async def _analyze_stakeholders(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Analyze and map project stakeholders."""
        self.logger.info("Starting stakeholder analysis")
        
        project_description = task_data.get("project_description", "")
        known_stakeholders = task_data.get("known_stakeholders", [])
        
        # Identify stakeholders from project description
        identified_stakeholders = await self._identify_stakeholders(project_description)
        
        # Combine with known stakeholders
        all_stakeholders = known_stakeholders + identified_stakeholders
        
        # Analyze stakeholder relationships and influence
        stakeholder_map = await self._create_stakeholder_map(all_stakeholders)
        
        # Store in memory
        await self.memory.store_context(
            context_type="stakeholder_analysis",
            content={
                "stakeholders": stakeholder_map,
                "total_count": len(all_stakeholders),
                "key_stakeholders": [s for s in stakeholder_map if s.get("influence") == "high"]
            },
            memory_type=MemoryType.LONG_TERM,
            importance=0.8
        )
        
        return TaskResult(
            success=True,
            result={
                "stakeholder_map": stakeholder_map,
                "summary": {
                    "total_stakeholders": len(all_stakeholders),
                    "key_stakeholders": len([s for s in stakeholder_map if s.get("influence") == "high"]),
                    "stakeholder_types": list(set(s.get("type", "unknown") for s in stakeholder_map))
                }
            },
            metadata={"task_type": "stakeholder_analysis"}
        )
    
    async def _identify_stakeholders(self, project_description: str) -> List[Dict[str, Any]]:
        """Identify stakeholders from project description."""
        prompt = f"""
        Based on the following project description, identify all potential stakeholders:
        
        Project Description:
        {project_description}
        
        For each stakeholder, provide:
        - Name/Role
        - Type (internal/external, primary/secondary)
        - Interest in the project
        - Influence level (high/medium/low)
        - Potential concerns or requirements
        """
        
        try:
            response = await self.generate_response(prompt)
            stakeholders = await self._parse_stakeholder_response(response)
            return stakeholders
        except Exception as e:
            self.logger.error(f"Failed to identify stakeholders: {str(e)}")
            return []
    
    async def _create_stakeholder_map(self, stakeholders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a comprehensive stakeholder map."""
        stakeholder_map = []
        
        for stakeholder in stakeholders:
            mapped_stakeholder = {
                "id": f"SH-{len(stakeholder_map) + 1:03d}",
                "name": stakeholder.get("name", "Unknown"),
                "role": stakeholder.get("role", "Unknown"),
                "type": stakeholder.get("type", "unknown"),
                "influence": stakeholder.get("influence", "medium"),
                "interest": stakeholder.get("interest", "medium"),
                "concerns": stakeholder.get("concerns", []),
                "requirements": stakeholder.get("requirements", []),
                "communication_preference": stakeholder.get("communication_preference", "email"),
                "created_at": datetime.utcnow().isoformat()
            }
            stakeholder_map.append(mapped_stakeholder)
        
        return stakeholder_map
    
    async def _parse_stakeholder_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured stakeholder data."""
        # Simplified parser - would need more sophisticated parsing in practice
        stakeholders = []
        
        lines = response.split('\n')
        current_stakeholder = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if any(keyword in line.lower() for keyword in ['stakeholder', 'role:', 'name:']):
                if current_stakeholder:
                    stakeholders.append(current_stakeholder)
                
                current_stakeholder = {
                    "name": line,
                    "type": "unknown",
                    "influence": "medium",
                    "interest": "medium",
                    "concerns": [],
                    "requirements": []
                }
        
        if current_stakeholder:
            stakeholders.append(current_stakeholder)
        
        return stakeholders
    
    async def _define_scope(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Define project scope based on requirements and constraints."""
        self.logger.info("Starting scope definition")
        
        # Get requirements from memory or task data
        requirements = task_data.get("requirements", [])
        if not requirements:
            req_context = await self.memory.get_context(context_type="requirements_gathering", limit=1)
            if req_context:
                requirements = req_context[0].get("content", {}).get("requirements", [])
        
        constraints = task_data.get("constraints", [])
        timeline = task_data.get("timeline", {})
        budget = task_data.get("budget", {})
        
        # Define scope boundaries
        scope_definition = await self._create_scope_definition(requirements, constraints, timeline, budget)
        
        # Store in memory
        await self.memory.store_context(
            context_type="scope_definition",
            content=scope_definition,
            memory_type=MemoryType.LONG_TERM,
            importance=0.9
        )
        
        return TaskResult(
            success=True,
            result=scope_definition,
            metadata={"task_type": "scope_definition"}
        )
    
    async def _create_scope_definition(
        self,
        requirements: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        timeline: Dict[str, Any],
        budget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comprehensive scope definition."""
        return {
            "in_scope": await self._define_in_scope(requirements),
            "out_of_scope": await self._define_out_of_scope(requirements, constraints),
            "assumptions": await self._identify_assumptions(requirements, constraints),
            "constraints": constraints,
            "deliverables": await self._define_deliverables(requirements),
            "success_criteria": await self._extract_success_criteria(requirements),
            "timeline": timeline,
            "budget": budget,
            "risks": await self._identify_scope_risks(requirements, constraints),
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _define_in_scope(self, requirements: List[Dict[str, Any]]) -> List[str]:
        """Define what is included in the project scope."""
        in_scope = []
        
        for req in requirements:
            if req.get("priority") in ["high", "medium"]:
                in_scope.append(req.get("description", ""))
        
        return in_scope
    
    async def _define_out_of_scope(
        self,
        requirements: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]]
    ) -> List[str]:
        """Define what is explicitly excluded from the project scope."""
        out_of_scope = []
        
        # Low priority requirements might be out of scope
        for req in requirements:
            if req.get("priority") == "low":
                out_of_scope.append(f"Low priority: {req.get('description', '')}")
        
        # Add constraint-based exclusions
        for constraint in constraints:
            if constraint.get("type") == "exclusion":
                out_of_scope.append(constraint.get("description", ""))
        
        return out_of_scope
    
    async def _identify_assumptions(
        self,
        requirements: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify project assumptions."""
        assumptions = [
            "Stakeholders will be available for regular feedback",
            "Required resources will be allocated as planned",
            "External dependencies will be delivered on time",
            "Technical requirements are feasible with current technology"
        ]
        
        return assumptions
    
    async def _define_deliverables(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Define project deliverables based on requirements."""
        deliverables = []
        
        # Group requirements into logical deliverables
        functional_reqs = [r for r in requirements if r.get("category") == "functional"]
        if functional_reqs:
            deliverables.append({
                "name": "Core Application",
                "description": "Main application functionality",
                "type": "software",
                "requirements": [r.get("id") for r in functional_reqs]
            })
        
        doc_reqs = [r for r in requirements if "documentation" in r.get("description", "").lower()]
        if doc_reqs:
            deliverables.append({
                "name": "Documentation",
                "description": "User and technical documentation",
                "type": "documentation",
                "requirements": [r.get("id") for r in doc_reqs]
            })
        
        return deliverables
    
    async def _extract_success_criteria(self, requirements: List[Dict[str, Any]]) -> List[str]:
        """Extract success criteria from requirements."""
        success_criteria = []
        
        for req in requirements:
            if req.get("priority") == "high":
                success_criteria.append(f"Successfully implement: {req.get('description', '')}")
        
        return success_criteria
    
    async def _identify_scope_risks(
        self,
        requirements: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify risks related to project scope."""
        risks = [
            {
                "type": "scope_creep",
                "description": "Requirements may expand beyond initial scope",
                "probability": "medium",
                "impact": "high"
            },
            {
                "type": "requirement_changes",
                "description": "Stakeholders may change requirements during development",
                "probability": "medium",
                "impact": "medium"
            }
        ]
        
        return risks
    
    async def _identify_risks(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Identify project risks."""
        self.logger.info("Starting risk identification")
        
        project_description = task_data.get("project_description", "")
        requirements = task_data.get("requirements", [])
        constraints = task_data.get("constraints", [])
        
        # Identify various types of risks
        technical_risks = await self._identify_technical_risks(requirements)
        business_risks = await self._identify_business_risks(project_description)
        resource_risks = await self._identify_resource_risks(constraints)
        timeline_risks = await self._identify_timeline_risks(requirements)
        
        all_risks = technical_risks + business_risks + resource_risks + timeline_risks
        
        # Assess and prioritize risks
        assessed_risks = await self._assess_risks(all_risks)
        
        # Store in memory
        await self.memory.store_context(
            context_type="risk_identification",
            content={
                "risks": assessed_risks,
                "risk_categories": ["technical", "business", "resource", "timeline"],
                "high_risk_count": len([r for r in assessed_risks if r.get("risk_level") == "high"])
            },
            memory_type=MemoryType.LONG_TERM,
            importance=0.8
        )
        
        return TaskResult(
            success=True,
            result={
                "risks": assessed_risks,
                "summary": {
                    "total_risks": len(assessed_risks),
                    "high_risk_count": len([r for r in assessed_risks if r.get("risk_level") == "high"]),
                    "risk_categories": ["technical", "business", "resource", "timeline"]
                }
            },
            metadata={"task_type": "risk_identification"}
        )
    
    async def _identify_technical_risks(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify technical risks from requirements."""
        risks = []
        
        # Analyze requirements for technical complexity
        for req in requirements:
            if any(keyword in req.get("description", "").lower() 
                   for keyword in ["integration", "api", "database", "performance", "security"]):
                risks.append({
                    "id": f"TECH-{len(risks) + 1:03d}",
                    "category": "technical",
                    "description": f"Technical complexity in: {req.get('description', '')}",
                    "probability": "medium",
                    "impact": "medium",
                    "related_requirement": req.get("id")
                })
        
        return risks
    
    async def _identify_business_risks(self, project_description: str) -> List[Dict[str, Any]]:
        """Identify business risks from project description."""
        risks = [
            {
                "id": "BUS-001",
                "category": "business",
                "description": "Market conditions may change during development",
                "probability": "low",
                "impact": "high"
            },
            {
                "id": "BUS-002",
                "category": "business",
                "description": "Stakeholder priorities may shift",
                "probability": "medium",
                "impact": "medium"
            }
        ]
        
        return risks
    
    async def _identify_resource_risks(self, constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify resource-related risks."""
        risks = []
        
        for constraint in constraints:
            if constraint.get("type") in ["budget", "timeline", "resources"]:
                risks.append({
                    "id": f"RES-{len(risks) + 1:03d}",
                    "category": "resource",
                    "description": f"Resource constraint: {constraint.get('description', '')}",
                    "probability": "medium",
                    "impact": "high"
                })
        
        return risks
    
    async def _identify_timeline_risks(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify timeline-related risks."""
        risks = [
            {
                "id": "TIME-001",
                "category": "timeline",
                "description": "Complex requirements may take longer than estimated",
                "probability": "medium",
                "impact": "medium"
            }
        ]
        
        return risks
    
    async def _assess_risks(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess and prioritize risks."""
        risk_matrix = {
            ("high", "high"): "critical",
            ("high", "medium"): "high",
            ("high", "low"): "medium",
            ("medium", "high"): "high",
            ("medium", "medium"): "medium",
            ("medium", "low"): "low",
            ("low", "high"): "medium",
            ("low", "medium"): "low",
            ("low", "low"): "low"
        }
        
        for risk in risks:
            probability = risk.get("probability", "medium")
            impact = risk.get("impact", "medium")
            risk["risk_level"] = risk_matrix.get((probability, impact), "medium")
            risk["created_at"] = datetime.utcnow().isoformat()
        
        # Sort by risk level
        risk_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        risks.sort(key=lambda x: risk_order.get(x.get("risk_level", "medium"), 2), reverse=True)
        
        return risks
    
    async def _analyze_constraints(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Analyze project constraints."""
        self.logger.info("Starting constraint analysis")
        
        constraints = task_data.get("constraints", [])
        project_description = task_data.get("project_description", "")
        
        # Identify additional constraints from project description
        identified_constraints = await self._identify_constraints(project_description)
        all_constraints = constraints + identified_constraints
        
        # Categorize constraints
        categorized_constraints = await self._categorize_constraints(all_constraints)
        
        # Analyze constraint impacts
        constraint_analysis = await self._analyze_constraint_impacts(categorized_constraints)
        
        # Store in memory
        await self.memory.store_context(
            context_type="constraint_analysis",
            content={
                "constraints": constraint_analysis,
                "categories": list(categorized_constraints.keys()),
                "total_count": len(all_constraints)
            },
            memory_type=MemoryType.LONG_TERM,
            importance=0.7
        )
        
        return TaskResult(
            success=True,
            result={
                "constraints": constraint_analysis,
                "summary": {
                    "total_constraints": len(all_constraints),
                    "categories": list(categorized_constraints.keys()),
                    "critical_constraints": len([c for c in all_constraints if c.get("severity") == "high"])
                }
            },
            metadata={"task_type": "constraint_analysis"}
        )
    
    async def _identify_constraints(self, project_description: str) -> List[Dict[str, Any]]:
        """Identify constraints from project description."""
        # This would use AI to identify implicit constraints
        constraints = [
            {
                "type": "budget",
                "description": "Project must be completed within allocated budget",
                "severity": "high"
            },
            {
                "type": "timeline",
                "description": "Project has fixed delivery deadline",
                "severity": "high"
            },
            {
                "type": "technology",
                "description": "Must use existing technology stack",
                "severity": "medium"
            }
        ]
        
        return constraints
    
    async def _categorize_constraints(self, constraints: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize constraints by type."""
        categories = {}
        
        for constraint in constraints:
            constraint_type = constraint.get("type", "other")
            if constraint_type not in categories:
                categories[constraint_type] = []
            categories[constraint_type].append(constraint)
        
        return categories
    
    async def _analyze_constraint_impacts(self, categorized_constraints: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze the impact of constraints on the project."""
        analyzed_constraints = {}
        
        for category, constraints in categorized_constraints.items():
            analyzed_constraints[category] = []
            
            for constraint in constraints:
                analyzed_constraint = {
                    **constraint,
                    "id": f"CON-{len(analyzed_constraints[category]) + 1:03d}",
                    "impact_areas": await self._identify_constraint_impacts(constraint),
                    "mitigation_strategies": await self._suggest_mitigation_strategies(constraint),
                    "created_at": datetime.utcnow().isoformat()
                }
                analyzed_constraints[category].append(analyzed_constraint)
        
        return analyzed_constraints
    
    async def _identify_constraint_impacts(self, constraint: Dict[str, Any]) -> List[str]:
        """Identify areas impacted by a constraint."""
        constraint_type = constraint.get("type", "")
        
        impact_mapping = {
            "budget": ["resource allocation", "scope", "quality"],
            "timeline": ["scope", "resource allocation", "quality"],
            "technology": ["architecture", "development approach", "integration"],
            "regulatory": ["compliance", "security", "documentation"],
            "resource": ["timeline", "scope", "quality"]
        }
        
        return impact_mapping.get(constraint_type, ["unknown"])
    
    async def _suggest_mitigation_strategies(self, constraint: Dict[str, Any]) -> List[str]:
        """Suggest strategies to mitigate constraint impacts."""
        constraint_type = constraint.get("type", "")
        
        strategy_mapping = {
            "budget": ["Prioritize high-value features", "Consider phased delivery", "Optimize resource allocation"],
            "timeline": ["Reduce scope", "Increase resources", "Parallel development"],
            "technology": ["Evaluate alternatives", "Plan integration carefully", "Prototype early"],
            "regulatory": ["Engage compliance early", "Regular reviews", "Expert consultation"],
            "resource": ["Cross-training", "External contractors", "Scope adjustment"]
        }
        
        return strategy_mapping.get(constraint_type, ["Monitor closely", "Regular review"])
    
    async def _define_success_criteria(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Define project success criteria."""
        self.logger.info("Starting success criteria definition")
        
        requirements = task_data.get("requirements", [])
        stakeholders = task_data.get("stakeholders", [])
        business_goals = task_data.get("business_goals", [])
        
        # Define different types of success criteria
        success_criteria = {
            "functional": await self._define_functional_criteria(requirements),
            "business": await self._define_business_criteria(business_goals),
            "stakeholder": await self._define_stakeholder_criteria(stakeholders),
            "technical": await self._define_technical_criteria(requirements),
            "quality": await self._define_quality_criteria()
        }
        
        # Store in memory
        await self.memory.store_context(
            context_type="success_criteria",
            content=success_criteria,
            memory_type=MemoryType.LONG_TERM,
            importance=0.9
        )
        
        return TaskResult(
            success=True,
            result=success_criteria,
            metadata={"task_type": "success_criteria"}
        )
    
    async def _define_functional_criteria(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Define functional success criteria."""
        criteria = []
        
        for req in requirements:
            if req.get("category") == "functional" and req.get("priority") in ["high", "medium"]:
                criteria.append({
                    "id": f"FC-{len(criteria) + 1:03d}",
                    "description": f"Successfully implement: {req.get('description', '')}",
                    "measurement": "Feature is implemented and tested",
                    "target": "100% of high priority functional requirements",
                    "related_requirement": req.get("id")
                })
        
        return criteria
    
    async def _define_business_criteria(self, business_goals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Define business success criteria."""
        criteria = [
            {
                "id": "BC-001",
                "description": "Project delivered on time and within budget",
                "measurement": "Timeline and budget adherence",
                "target": "±10% of planned timeline and budget"
            },
            {
                "id": "BC-002",
                "description": "Stakeholder satisfaction achieved",
                "measurement": "Stakeholder feedback scores",
                "target": "Average satisfaction score ≥ 4.0/5.0"
            }
        ]
        
        return criteria
    
    async def _define_stakeholder_criteria(self, stakeholders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Define stakeholder-specific success criteria."""
        criteria = []
        
        for stakeholder in stakeholders:
            if stakeholder.get("influence") == "high":
                criteria.append({
                    "id": f"SC-{len(criteria) + 1:03d}",
                    "description": f"Meet requirements of {stakeholder.get('name', 'stakeholder')}",
                    "measurement": "Stakeholder acceptance",
                    "target": "Formal acceptance from key stakeholder",
                    "stakeholder_id": stakeholder.get("id")
                })
        
        return criteria
    
    async def _define_technical_criteria(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Define technical success criteria."""
        criteria = [
            {
                "id": "TC-001",
                "description": "System performance meets requirements",
                "measurement": "Performance testing results",
                "target": "Response time < 2 seconds for 95% of requests"
            },
            {
                "id": "TC-002",
                "description": "System reliability achieved",
                "measurement": "Uptime monitoring",
                "target": "99.9% uptime"
            },
            {
                "id": "TC-003",
                "description": "Security requirements met",
                "measurement": "Security audit results",
                "target": "No critical security vulnerabilities"
            }
        ]
        
        return criteria
    
    async def _define_quality_criteria(self) -> List[Dict[str, Any]]:
        """Define quality success criteria."""
        criteria = [
            {
                "id": "QC-001",
                "description": "Code quality standards met",
                "measurement": "Code review and static analysis",
                "target": "Code coverage ≥ 80%, no critical code smells"
            },
            {
                "id": "QC-002",
                "description": "Documentation completeness",
                "measurement": "Documentation review",
                "target": "All user and technical documentation complete"
            },
            {
                "id": "QC-003",
                "description": "Testing coverage achieved",
                "measurement": "Test execution results",
                "target": "All test cases pass, coverage ≥ 80%"
            }
        ]
        
        return criteria
