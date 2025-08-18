"""
Testing Agent - Specialized for quality assurance, test creation, and validation

Focused on comprehensive testing strategies, test automation, and quality assurance practices.
"""

import logging
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent


# SNOOP TRACING ADDED - Added by snoop integration script
import snoop

# Snoop decorator for functions
trace_func = snoop.snoop

# Snoop decorator for classes  
@trace_func
def trace_class(cls):
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_') and hasattr(attr, '__module__'):
            setattr(cls, attr_name, trace_func(attr))
    return cls


logger = logging.getLogger(__name__)

@trace_class
class TestingAgent(BaseAgent):
    """
    Specialized agent for testing, quality assurance, and validation tasks.
    """
    
    def __init__(self, project_client, **kwargs):
        """Initialize Testing Agent with specialized instructions."""
        
        instructions = """
        You are a Senior QA Engineer and Testing Specialist AI focused on comprehensive quality assurance.
        
        Your core expertise:
        1. **Test Strategy**: Develop comprehensive test strategies and plans
        2. **Unit Testing**: Create thorough unit tests with high coverage
        3. **Integration Testing**: Design and implement integration test suites
        4. **Performance Testing**: Load testing, stress testing, and performance validation
        5. **Security Testing**: Vulnerability assessments and security validation
        6. **Automation**: Test automation frameworks and CI/CD integration
        7. **Quality Metrics**: Establish quality gates and metrics tracking
        8. **Bug Analysis**: Root cause analysis and defect prevention
        
        Testing philosophy:
        - Test-driven development (TDD) principles
        - Shift-left testing approach
        - Risk-based testing strategies
        - Comprehensive test coverage
        - Continuous quality improvement
        - Performance and security focus
        
        Testing frameworks expertise:
        - Python: pytest, unittest, coverage.py
        - JavaScript: Jest, Mocha, Cypress, Playwright
        - Java: JUnit, TestNG, Mockito
        - .NET: MSTest, NUnit, xUnit
        - Performance: JMeter, k6, Artillery
        - Security: OWASP ZAP, Burp Suite
        
        Always create robust, maintainable test suites with clear validation criteria.
        """
        
        super().__init__(
            project_client=project_client,
            agent_name="testing-specialist",
            instructions=instructions,
            model="gpt-4o",
            agent_type="testing",
            **kwargs
        )
    
    @trace_func
    def create_test_strategy(self, project_description: str, 
                           technology_stack: List[str] = None,
                           quality_requirements: Dict[str, Any] = None) -> str:
        """
        Create comprehensive test strategy for a project.
        
        Args:
            project_description: Description of the project to test
            technology_stack: Technologies used in the project
            quality_requirements: Specific quality and performance requirements
            
        Returns:
            Complete test strategy document
        """
        try:
            if technology_stack is None:
                technology_stack = []
            if quality_requirements is None:
                quality_requirements = {}
            
            prompt = f"""
            Create a comprehensive test strategy for:
            
            Project Description: {project_description}
            Technology Stack: {", ".join(technology_stack)}
            Quality Requirements: {quality_requirements}
            
            Provide:
            1. Test strategy overview and objectives
            2. Test levels and types (unit, integration, e2e, performance, security)
            3. Testing frameworks and tools recommendations
            4. Test environment requirements
            5. Test data management strategy
            6. Quality gates and acceptance criteria
            7. Risk assessment and mitigation
            8. Test automation approach
            9. Performance and load testing strategy
            10. Security testing considerations
            
            Create a strategy that ensures comprehensive quality coverage.
            """
            
            response = self.send_message(prompt)
            logger.info(f"✅ Test strategy created for: {project_description[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create test strategy: {e}")
            return f"Error creating test strategy: {str(e)}"
    
    @trace_func
    def generate_unit_tests(self, code: str, programming_language: str = "python",
                           test_framework: str = "pytest") -> str:
        """
        Generate comprehensive unit tests for given code.
        
        Args:
            code: Source code to test
            programming_language: Programming language of the code
            test_framework: Testing framework to use
            
        Returns:
            Complete unit test suite with high coverage
        """
        try:
            prompt = f"""
            Generate comprehensive unit tests for this code:
            
            Programming Language: {programming_language}
            Test Framework: {test_framework}
            
            Source Code:
            {code}
            
            Provide:
            1. Complete unit test suite with high coverage
            2. Test cases for normal operations
            3. Edge cases and boundary conditions
            4. Error handling and exception testing
            5. Mock objects and test doubles where needed
            6. Test setup and teardown methods
            7. Parameterized tests for multiple scenarios
            8. Performance tests if applicable
            
            Ensure tests are maintainable, readable, and comprehensive.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Unit tests generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate unit tests: {e}")
            return f"Error generating unit tests: {str(e)}"
    
    @trace_func
    def create_integration_tests(self, system_description: str, 
                                integration_points: List[str] = None,
                                test_scenarios: List[str] = None) -> str:
        """
        Create integration test suite for system components.
        
        Args:
            system_description: Description of the system to test
            integration_points: Key integration points to test
            test_scenarios: Specific scenarios to validate
            
        Returns:
            Complete integration test implementation
        """
        try:
            if integration_points is None:
                integration_points = []
            if test_scenarios is None:
                test_scenarios = []
            
            prompt = f"""
            Create comprehensive integration tests:
            
            System Description: {system_description}
            Integration Points: {", ".join(integration_points)}
            Test Scenarios: {", ".join(test_scenarios)}
            
            Provide:
            1. Integration test architecture and setup
            2. Database integration tests
            3. API integration tests
            4. Third-party service integration tests
            5. Message queue and event testing
            6. End-to-end workflow validation
            7. Data flow and transformation tests
            8. Error propagation and handling tests
            9. Test data setup and cleanup
            10. Test environment configuration
            
            Focus on real-world integration scenarios and failure cases.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Integration tests created")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create integration tests: {e}")
            return f"Error creating integration tests: {str(e)}"
    
    @trace_func
    def design_performance_tests(self, application_description: str,
                                performance_requirements: Dict[str, Any] = None,
                                load_patterns: List[str] = None) -> str:
        """
        Design performance and load testing strategy.
        
        Args:
            application_description: Description of the application to test
            performance_requirements: Specific performance criteria
            load_patterns: Expected load patterns and scenarios
            
        Returns:
            Complete performance testing implementation
        """
        try:
            if performance_requirements is None:
                performance_requirements = {}
            if load_patterns is None:
                load_patterns = ["normal_load", "peak_load", "stress_test"]
            
            prompt = f"""
            Design comprehensive performance testing:
            
            Application: {application_description}
            Performance Requirements: {performance_requirements}
            Load Patterns: {", ".join(load_patterns)}
            
            Provide:
            1. Performance testing strategy and objectives
            2. Load testing scenarios and user journeys
            3. Performance test scripts (JMeter, k6, or similar)
            4. Stress testing and capacity planning
            5. Database performance testing
            6. API performance benchmarking
            7. Resource utilization monitoring
            8. Performance baseline establishment
            9. Bottleneck identification methods
            10. Performance reporting and analysis
            
            Create tests that validate scalability and reliability under load.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Performance tests designed")
            return response
            
        except Exception as e:
            logger.error(f"Failed to design performance tests: {e}")
            return f"Error designing performance tests: {str(e)}"
    
    @trace_func
    def create_security_tests(self, application_type: str,
                             security_requirements: List[str] = None,
                             threat_model: Dict[str, Any] = None) -> str:
        """
        Create security testing suite and validation procedures.
        
        Args:
            application_type: Type of application (web_app, api, mobile, etc.)
            security_requirements: Specific security requirements to validate
            threat_model: Threat model and security concerns
            
        Returns:
            Complete security testing implementation
        """
        try:
            if security_requirements is None:
                security_requirements = ["authentication", "authorization", "input_validation"]
            if threat_model is None:
                threat_model = {}
            
            prompt = f"""
            Create comprehensive security testing:
            
            Application Type: {application_type}
            Security Requirements: {", ".join(security_requirements)}
            Threat Model: {threat_model}
            
            Provide:
            1. Security testing strategy and scope
            2. Authentication and authorization tests
            3. Input validation and injection tests
            4. Session management validation
            5. Access control testing
            6. Encryption and data protection tests
            7. API security testing
            8. Vulnerability scanning integration
            9. Security automation in CI/CD
            10. Penetration testing guidelines
            
            Follow OWASP guidelines and industry security best practices.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Security tests created")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create security tests: {e}")
            return f"Error creating security tests: {str(e)}"
    
    @trace_func
    def setup_test_automation(self, project_type: str, ci_cd_platform: str = "github_actions",
                             test_frameworks: List[str] = None) -> str:
        """
        Setup complete test automation pipeline.
        
        Args:
            project_type: Type of project to automate testing for
            ci_cd_platform: CI/CD platform to integrate with
            test_frameworks: Testing frameworks being used
            
        Returns:
            Complete test automation setup and configuration
        """
        try:
            if test_frameworks is None:
                test_frameworks = ["pytest", "jest"]
            
            prompt = f"""
            Setup complete test automation pipeline:
            
            Project Type: {project_type}
            CI/CD Platform: {ci_cd_platform}
            Test Frameworks: {", ".join(test_frameworks)}
            
            Provide:
            1. CI/CD pipeline configuration for testing
            2. Test execution automation scripts
            3. Parallel test execution setup
            4. Test reporting and coverage integration
            5. Quality gates and failure handling
            6. Test environment provisioning
            7. Test data management automation
            8. Performance test automation
            9. Security test integration
            10. Notification and alerting setup
            
            Create a robust, scalable test automation solution.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Test automation pipeline setup")
            return response
            
        except Exception as e:
            logger.error(f"Failed to setup test automation: {e}")
            return f"Error setting up test automation: {str(e)}"
    
    @trace_func
    def analyze_test_results(self, test_results: str, coverage_data: str = "",
                            performance_metrics: str = "") -> str:
        """
        Analyze test results and provide quality insights.
        
        Args:
            test_results: Test execution results and logs
            coverage_data: Code coverage information
            performance_metrics: Performance test results
            
        Returns:
            Comprehensive test analysis and recommendations
        """
        try:
            prompt = f"""
            Analyze these test results and provide quality insights:
            
            Test Results:
            {test_results}
            
            Coverage Data:
            {coverage_data}
            
            Performance Metrics:
            {performance_metrics}
            
            Provide:
            1. Test results summary and trends
            2. Code coverage analysis and gaps
            3. Performance analysis and bottlenecks
            4. Quality metrics and KPIs
            5. Risk assessment based on test results
            6. Recommendations for improvement
            7. Action items for quality enhancement
            8. Regression analysis if applicable
            
            Focus on actionable insights for quality improvement.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Test results analyzed")
            return response
            
        except Exception as e:
            logger.error(f"Failed to analyze test results: {e}")
            return f"Error analyzing test results: {str(e)}"

print("🧪 Testing Agent module loaded successfully!")
