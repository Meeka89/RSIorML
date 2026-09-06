1. Research idea:  
   1. This project will investigate how language models respond to unauthorized model distillation, extraction, and recursive self-improvement. As models become stronger in coding, reasoning, and data generation, there is a growing concern that users may try to use models to advance development in other AIs in unsafe or unauthorized ways.  
   2. But at the same time, many of the topics are legitimate prompts from machine learning research. Students, researchers, and developers ask questions about distillation, model compression, alignment, fine-tuning, or AI safety. The boundary between education about AI and misuse of AI is often context-dependent.  
   3. The main research question is: Can open-weight LLMs use conversational context to distinguish legitimate AI research from requests that may lead to model extraction, unsafe distillation, or recursive self-improvement?  
   4. This project will focus on responsibly studying AI security perspectives in controlled experiments, open models, published research and ethical analysis. The goal is to better understand the risks of model imitation and identify practical strategies for evaluating and improving AI safety systems.  
2. Why the problem matters:  
   1. AI systems are already being used by companies to develop updates or fix bugs in their own models. This use of AI-assisted AI development can create the conditions for someone else to misuse the power of AI to train, copy, or improve another model.  
   2. If safeguards are too strict, real educational prompts can get over-refused, or redirected unnecessarily. This can make the model less beneficial for students or researchers. The ideal behavior is to not to automatically refuse any request related to the field of AI, but rather understand the context, ask clarifying questions, and redirect unsafe requests.  
   3. This matters because future AI will need to reason about intent, authorization, model ownership, training data permissions, and whether the request is asking for conceptual understanding or operational misuse. Existing safety benchmarks often focus on broad harmful-content refusal, jailbreaks, or over-refusal. Fewer benchmarks focus on the gray area between AI research and AI-improvement misuse. Studying this boundary could contribute to safer and more useful AI systems.  
3. What I hope to investigate, Build, Test, or Discover  
   1. I hope to build a small benchmark that tests how language models respond to prompts about knowledge distillation, model extraction, safety-removal fine-tuning, and self-improvement.  
   2. The benchmark could include several categories of prompts:  
      1. Clearly legitimate AI research prompts  
      2. Clearly unsafe AI-improvement prompts  
      3. Ambiguous single-turn prompts  
      4. Multi-turn context-shift prompts  
   3. The most important part of the project would be testing whether models can use context across conversations. For example, a conversation might begin as normal questions about distillation but start shifting towards unauthorized model imitation or avoiding detection. This would test the model's ability to recognize the context shift from legitimate to potentially unsafe or unauthorized.  
4. Relevant Background, Tools, Datasets, or Methods  
   1. This project will require background research in:  
      1. Distillation and model compression  
      2. Model extraction  
      3. Recursive self-improvement and AI R\&D acceleration  
      4. AI safety benchmarks  
      5. Over-refusal/under-refusal in language models  
      6. Instruction tuning and alignment behavior  
   2. The project would mostly use open-weight models. I would create a labeled dataset of prompts and conversations. Each item would have an expected response type, such as:  
      1. Normal helpful response  
      2. Clarifying response  
      3. Safe redirection  
      4. Refusal  
   3. The evaluation would measure model behavior using metrics such as:  
      1. False refusals on legitimate AI research prompts  
      2. False compliance rate on suspicious AI-improvement prompts  
      3. Clarification rate on ambiguous prompts  
      4. Safe redirect on risky prompts  
      5. Consistency across paraphrased prompts  
      6. Performance difference between single-turn and multi-turn cases  
5. Potential Contribution or Artifact  
   1. The main contribution would be a benchmark and analysis of the results and a research paper explaining the motivation, benchmark design, methods, results, and implications.  
   2. Additional artifacts could include:   
      1. A dataset of prompts and multi-turn conversations  
      2. An evaluation rubric  
      3. Model comparison reports  
      4. Evaluation framework to be used on models.  
   3. This project would contribute by focusing on the underexplored safety boundary. Instead of seeing if models can refuse harmful prompts, this project explores whether models can distinguish between legitimate AI research prompts and prompts involving model extraction, unsafe distillation, or recursive self-improvement.