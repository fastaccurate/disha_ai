# File Upload Answer Type Assignment

## Overview

Implement a new answer type that allows users to upload files (e.g., PDF/images) as answers to assessment questions. The uploaded files should be evaluated using LLM-based evaluation.

## Important Notes

This assignment is meant to be a **close-to-real-world working example**. The codebase has:

- **Clear code patterns and conventions** that you should identify and follow
- **Some messy code in places**, which is typical of real-world codebases

Your task is to:

- Understand the existing patterns and conventions
- Implement your solution following those patterns as far as possible
- Ensure consistency with the codebase architecture

**Tool Usage**: You are encouraged to use AI tools, IDEs, code assistants, and other development tools as you would in a real-world scenario. However, you must be able to:

- Take full ownership of your code
- Explain your implementation appropriately
- Justify design decisions

## Objectives

1. Add a new `FILE_UPLOAD` answer type to the assessment system
2. Implement file upload functionality on the frontend
3. Store uploaded files securely
4. Evaluate uploaded files using LLM evaluation
5. Integrate the new answer type with the existing assessment flow
6. Create mock LLM testing functionality with properly structured JSON responses to enable testing without requiring a valid LLM API key

## Expected Outcomes

### Backend

- Users can submit file uploads as answers to questions
- Files are stored and can be retrieved later
- File content is extracted and processed for evaluation
- LLM evaluation evaluates the file content against the question
- Evaluation results are stored and can be retrieved
- Mock LLM testing functionality exists with properly structured JSON responses matching the expected format, allowing end-to-end testing without LLM API keys

### Frontend

- Users can upload files through an intuitive interface
- File upload progress and status are clearly indicated
- Users can see previously uploaded files for a question
- Error handling provides clear feedback to users
- The feature integrates seamlessly with the existing assessment UI

## Evaluation Criteria

The assignment will be evaluated based on:

1. **Functionality**

   - File upload works correctly
   - Files are stored and retrieved properly
   - LLM evaluation processes file content correctly
   - Complete integration with existing assessment flow

2. **Code Quality**

   - Follows existing code patterns and conventions
   - Clean, readable, well-commented code
   - Proper error handling
   - No breaking changes to existing functionality

3. **User Experience**

   - Intuitive file upload interface
   - Clear feedback during upload process
   - Helpful error messages
   - Smooth integration with assessment UI

4. **Testing & Edge Cases**
   - Handles various file types correctly
   - Validates file sizes and types appropriately
   - Handles errors gracefully
   - Edge cases are considered

## Deliverables

1. Working implementation with all code changes
2. Database migrations (if needed)
3. Brief documentation of the implementation approach
4. Mock LLM testing functionality with properly structured JSON responses

## Submission Requirements

**Final submission must include:**

1. **Pull Request (PR) Link**: Submit a PR link containing all code changes
2. **Video Demo**: A short video (2-5 minutes) demonstrating:
   - The working file upload assessment feature
   - High-level explanation of the overall flow
   - Overview of the changes implemented
   - How the mock LLM testing works

The video should clearly show the feature in action and explain your implementation approach.

---

**Good luck with the assignment!**
