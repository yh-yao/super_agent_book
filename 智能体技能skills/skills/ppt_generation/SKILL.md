# Skill: PPT Generation

## Name
ppt_generation

## Description
Generate a PowerPoint (.pptx) file from structured slide content.

## Category
Content Generation

## Inputs
- title: string  
- slides: list  
  - title: string  
  - content: list of strings  

## Outputs
- status: success | failure  
- file: path to generated pptx  
- slide_count: integer  

## Determinism
Deterministic (no randomness)

## Side Effects
Creates a local PowerPoint file
