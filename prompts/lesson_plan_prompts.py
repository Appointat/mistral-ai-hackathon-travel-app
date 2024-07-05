from camel.prompts import TextPrompt

LESSON_PLAN_PROMPT = TextPrompt("""
===== TASK =====
The task is to create a comprehensive lesson plan based on a given CONTENT OF ARTICEL in the field of machine learning. The lesson plan should be suitable for graduate-level students with a strong background in computer science and mathematics.

===== SPECS FOR LESSON PLAN =====
Based on the provided CONTENT OF ARTICEL, generate a detailed *lesson plan* following these specifications:

1. Article Analysis:
   a) Identify the main topic and key concepts presented in the article.
   b) List any prerequisite knowledge required to understand the content.
   c) Highlight the novelty or significance of the research presented.
2. Learning Objectives:
   a) Formulate 3-5 SMART (Specific, Measurable, Achievable, Relevant, Time-bound) learning objectives.
   b) Ensure objectives cover both theoretical understanding and practical application.
3. Lesson Structure (design a 3-hour session):
   a) Introduction (15 minutes):
      - Engage students with a hook related to the article's topic.
      - Briefly overview the article's context and importance.
   b) Theoretical Background (45 minutes):
      - Break down complex concepts from the article.
      - Explain mathematical foundations, if applicable.
   c) Main Content Presentation (60 minutes):
      - Detail the core methodology or algorithm presented in the article.
      - Illustrate with diagrams or pseudocode where appropriate.
   d) Practical Application (45 minutes):
      - Design a hands-on activity or coding exercise related to the article's content.
      - Specify tools or frameworks to be used (e.g., Python, TensorFlow, PyTorch).
   e) Discussion and Q&A (15 minutes):
      - Prepare thought-provoking questions about the article's implications.
      - Anticipate potential student questions and prepare answers.
4. Assessment Strategies:
   a) Formative Assessment:
      - Create 2-3 quick quiz questions to check understanding during the lesson.
   b) Summative Assessment:
      - Design a project or assignment that applies the article's concepts.
      - Develop a rubric for evaluating student performance.
5. Resources and Materials:
   a) List required reading materials (including the original article).
   b) Recommend supplementary resources (papers, videos, online courses).
   c) Specify any software or hardware requirements for practical sessions.
6. Adaptability and Differentiation:
   a) Suggest modifications for students with different levels of prior knowledge.
   b) Provide extension activities for advanced learners.
7. Real-world Connections:
   a) Provide examples of how the article's content applies to current industry problems.
   b) Discuss potential future research directions based on the article.
8. Interdisciplinary Connections:
   a) Highlight connections to other fields (e.g., statistics, neuroscience, computer vision).
   b) Suggest how the content could be relevant to non-ML domains.
9. Reflection and Feedback:
    a) Design a short reflective activity for students to consolidate their learning.
    b) Create a mechanism for collecting student feedback on the lesson.

""")

# https://bradleyboehmke.github.io/HOML/engineering.html
MACHINE_LEARNING_ARTICEL_PROMPT = TextPrompt("""
# Chapter 3: Feature & Target Engineering
## Introduction
- Data preprocessing and engineering techniques involve adding, deleting, or transforming data.
- Feature engineering can significantly impact an algorithm's predictive ability.
- The chapter covers fundamental preprocessing tasks that can improve modeling performance.
## 3.1 Prerequisites
- Required packages: dplyr, ggplot2, visdat, caret, recipes
## 3.2 Target Engineering
- Transforming the response variable can lead to predictive improvement, especially with parametric models.
- Example: Log transformation of Sale_Price in Ames housing data to minimize skewness.
- Two main approaches:
  1. Normalize with log transformation
  2. Use Box-Cox transformation
## 3.3 Dealing with Missingness
- Types of missingness: informative missingness and missingness at random
- Visualization of missing values using heat maps (e.g., geom_raster() or vis_miss())
- Imputation methods:
  1. Estimated statistic (mean, median, mode)
  2. K-nearest neighbor
  3. Tree-based (e.g., random forest, bagged trees)
## 3.4 Numeric Feature Engineering
- Skewness: Use Box-Cox or Yeo-Johnson transformations
- Standardization: Center and scale numeric features
## 3.5 Categorical Feature Engineering
- Lumping: Collapse infrequently occurring categories
- One-hot & dummy encoding: Convert categorical variables to numeric representations
- Label encoding: Numeric conversion of categorical levels (useful for ordinal variables)
## 3.6 Dimension Reduction
- Use techniques like Principal Component Analysis (PCA) to reduce the number of features
## 3.7 Proper Implementation
- Consider the order of preprocessing steps
- Perform feature engineering within each resampling iteration to avoid data leakage
- Use the recipes package to create a feature engineering blueprint
## 3.8 Putting the Process Together
- Create a feature engineering blueprint using recipe()
- Use prep() to estimate parameters based on training data
- Apply the blueprint to new data using bake()
- Integrate with caret's train() function for model training
## Example: Ames Housing Data
- Created a blueprint with the following steps:
  1. Remove near-zero variance features for categorical features
  2. Ordinally encode quality features
  3. Standardize numeric features
  4. One-hot encode remaining categorical features
- Applied the blueprint within caret's train() function
- Results showed improvement in prediction error
## Key Takeaways
- Feature engineering can significantly improve model performance
- The order of preprocessing steps is important
- Implement feature engineering within the resampling process to avoid data leakage
- Use tools like the recipes package to create reproducible feature engineering pipelines

=====
""")
