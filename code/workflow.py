import dspy
from typing import List, Dict
from dataclasses import dataclass

# 1. Data Structures
@dataclass
class CategoryExample:
    text: str
    label: str
    is_correct: bool

class CategorySignature(dspy.Signature):
    """Signature for classification task"""
    text = dspy.InputField()
    label = dspy.OutputField()

# 2. Prompt Optimizer
class PromptOptimizer(dspy.Program):
    def __init__(self, initial_prompt: str):
        self.predictor = dspy.Predict(CategorySignature)
        self.current_prompt = initial_prompt
        self.successful_examples = []
        self.failed_examples = []
    
    def forward(self, text: str) -> str:
        formatted_prompt = self.current_prompt.format(text=text)
        return self.predictor(text=formatted_prompt).label
    
    def learn_from_feedback(self, example: CategoryExample):
        if example.is_correct:
            self.successful_examples.append(example)
        else:
            self.failed_examples.append(example)
    
    def optimize_prompt(self) -> str:
        """Improve prompt based on successful and failed examples"""
        if not self.failed_examples:
            return self.current_prompt
            
        # Analyze patterns in successful vs failed examples
        success_patterns = self._analyze_patterns(self.successful_examples)
        failure_patterns = self._analyze_patterns(self.failed_examples)
        
        # Generate improved prompt
        improved_prompt = self._generate_improved_prompt(
            success_patterns,
            failure_patterns
        )
        
        self.current_prompt = improved_prompt
        return improved_prompt
    
    def _analyze_patterns(self, examples: List[CategoryExample]) -> Dict:
        """Analyze patterns in examples"""
        return {
            'common_features': self._extract_features(examples),
            'example_count': len(examples),
            'label_distribution': self._get_label_distribution(examples)
        }
    
    def _extract_features(self, examples: List[CategoryExample]) -> Dict:
        """Extract common features from examples"""
        # Implement feature extraction logic
        # This could analyze text length, complexity, key phrases, etc.
        return {}
    
    def _get_label_distribution(self, examples: List[CategoryExample]) -> Dict:
        """Get distribution of labels in examples"""
        distribution = {}
        for example in examples:
            distribution[example.label] = distribution.get(example.label, 0) + 1
        return distribution
    
    def _generate_improved_prompt(self, 
                                success_patterns: Dict, 
                                failure_patterns: Dict) -> str:
        """Generate improved prompt based on patterns"""
        # Implement prompt improvement logic
        # This could add clarifications, examples, or modify instructions
        return self.current_prompt  # Placeholder

# 3. Testing Framework
class OptimizationTester:
    def __init__(self, initial_prompt: str):
        self.optimizer = PromptOptimizer(initial_prompt)
        
    def run_optimization(self, training_data: List[CategoryExample]) -> Dict:
        results_history = []
        current_prompt = self.optimizer.current_prompt
        
        # Initial round
        round_results = self._evaluate_round(training_data)
        results_history.append({
            'prompt': current_prompt,
            'accuracy': round_results['accuracy'],
            'results': round_results['detailed']
        })
        
        # Learn from results and optimize
        for example in training_data:
            self.optimizer.learn_from_feedback(example)
        
        # Generate improved prompt
        improved_prompt = self.optimizer.optimize_prompt()
        
        # Test improved prompt
        self.optimizer.current_prompt = improved_prompt
        round_results = self._evaluate_round(training_data)
        results_history.append({
            'prompt': improved_prompt,
            'accuracy': round_results['accuracy'],
            'results': round_results['detailed']
        })
        
        return results_history
    
    def _evaluate_round(self, examples: List[CategoryExample]) -> Dict:
        correct = 0
        detailed_results = []
        
        for example in examples:
            prediction = self.optimizer(example.text)
            is_correct = (prediction == example.label)
            
            if is_correct:
                correct += 1
                
            detailed_results.append({
                'text': example.text,
                'true_label': example.label,
                'predicted': prediction,
                'correct': is_correct
            })
        
        return {
            'accuracy': correct / len(examples),
            'detailed': detailed_results
        }

# 4. Usage Example
def main():
    # Initial prompt template
    initial_prompt = """
    Task: Categorize the following text into positive, negative, or neutral.
    
    Text: {text}
    
    Please provide the category label only.
    """
    
    # Sample data
    training_data = [
        CategoryExample(
            text="This product exceeded all my expectations!",
            label="positive",
            is_correct=False
        ),
        CategoryExample(
            text="Complete waste of money and time.",
            label="negative",
            is_correct=False
        ),
        CategoryExample(
            text="It works as advertised, nothing more.",
            label="neutral",
            is_correct=False
        )
    ]
    
    # Run optimization
    tester = OptimizationTester(initial_prompt)
    results = tester.run_optimization(training_data)
    
    # Print results
    print("\nOptimization Results:")
    for i, round_result in enumerate(results):
        print(f"\nRound {i + 1}")
        print(f"Accuracy: {round_result['accuracy']:.2f}")
        print("Prompt:")
        print(round_result['prompt'])
        print("\nSample Results:")
        for result in round_result['results'][:2]:
            print(f"\nText: {result['text']}")
            print(f"True Label: {result['true_label']}")
            print(f"Predicted: {result['predicted']}")
            print(f"Correct: {result['correct']}")

if __name__ == "__main__":
    main()