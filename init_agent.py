from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from time import sleep
import os
import pandas as pd
import glob
import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any, Optional
class CandidateInfo(BaseModel):
    university: str  
    age: int
    college: str
    gender: str
    experience: int  
    department: str
    degrees:str
    skills: list[str]

class ExtractedData(BaseModel):
    candidates: list[CandidateInfo]


class ExtractAgent:    
    def __init__(self):
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Set up LLM and parsing components
        self.parser = PydanticOutputParser(pydantic_object=ExtractedData)
        self.llm = ChatGoogleGenerativeAI(
            model=os.environ["MODEL"],
            temperature=0.2,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.environ["GEMINI_API_KEY"]
        )
        self.llm_with_structured_output = self.llm.with_structured_output(ExtractedData)
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an efficient HR assistant responsible for accurately extracting and classifying key details from CVs. Extract the following structured information:
                - University: Extract and standardize the university name (e.g., "Stanford University" not "Stanford" or "Japan University" not "Egypt Japan University of Science and Technology").
                - College: Classify the field of study into one of these categories only: "Computer Science", "Engineering", or "Other".
                - Department: Extract the specific department specialization (e.g., "Security", "Computer Science", "Information Systems", "Software Engineering"). Only include real academic departments.
                - Age: Extract the candidate's age as a number.
                - Experience: Calculate total years of full-time professional work experience.
                - Gender: Extract stated gender (Female or Male).
                - Skills: Extract a comprehensive list of technical skills section mentioned in the CV.
                -Degrees Obtained: degree of candidate classify as (e.g., Bachelor's, Master's, PhD).
                Present all information in a structured format with proper capitalization for each field. Ensure responses are accurate, consistent, and follow standard naming conventions.
                """,
            ),
            ("human", "{cv}"),
        ])
        self.chain = self.prompt | self.llm_with_structured_output

    def read_pdf(self, file_path: str) -> str:
        """Read a PDF file and extract its text content."""
        try:
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])
            doc.close()  # Properly close the document
            return text
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return f"Error processing document: {file_path}"

    def get_pdfs_content(self, path: str) -> List[str]:
        """Get content from all PDF files in the specified directory."""
        self.logger.info(f"path of reading files is {path}")

        pdf_files = glob.glob(f"{path}/*.pdf")
        self.logger.info(f"Found {len(pdf_files)} PDF files in {path}")
        
        pdf_list = []
        for file in pdf_files:
            self.logger.info(f"Reading {file}")
            pdf_list.append(self.read_pdf(file))
        
        return pdf_list

    def get_data_as_dict(self, extracted_data_list: List[Dict[str, Any]]) -> Dict[str, List]:
        """Flattens the extracted candidate information into a dictionary."""
        candidate_keys = CandidateInfo.model_fields

        # Initialize structured data with appropriate default types
        structured_data = {
            key: [] for key in candidate_keys
        }

        if not extracted_data_list:
            return structured_data

        # Loop through batches of extracted data
        for batch in extracted_data_list:
            candidates = batch.get("candidates", [])
            if not candidates:
                continue

            # Loop through each candidate entry
            for candidate in candidates:
                for key, field_info in candidate_keys.items():
                    field_type = field_info.annotation  # Get expected type
                    missing_value=0
                    # Assign default values based on type if missing
                    if field_type == int:
                        missing_value = 0
                    elif field_type == list or field_type == List[str]:  # Handle lists
                        missing_value = []
                    else:  # Default to "Unknown" for strings and other types
                        missing_value = "Unknown"
                    value = candidate.get(key,missing_value)

                    structured_data[key].append(value)

        return structured_data

    def generate_data(self, pdf_list: List[str]) -> pd.DataFrame:
        """Processes CVs in batches and extracts structured information."""
        extracted_data_list = []
        batch_size = 3
        total_batches = (len(pdf_list) + batch_size - 1) // batch_size
        
        self.logger.info(f"Processing {len(pdf_list)} CVs in {total_batches} batches")
        
        for batch_idx, i in enumerate(range(0, len(pdf_list), batch_size)):
            cv_chunk = pdf_list[i:i + batch_size]
            self.logger.info(f"Processing batch {batch_idx + 1}/{total_batches} ({len(cv_chunk)} CVs)")
            
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = self.chain.invoke({"cv": "\n\n\n".join(cv_chunk)}).dict()
                    extracted_data_list.append(response)
                    self.logger.info(f"Successfully processed batch {batch_idx + 1}")
                    break
                except Exception as e:
                    retry_count += 1
                    self.logger.error(f"Error in batch {batch_idx + 1} (attempt {retry_count}/{max_retries}): {e}")
                    if retry_count < max_retries:
                        sleep_time = 10 * retry_count  # Exponential backoff
                        self.logger.info(f"Retrying in {sleep_time} seconds...")
                        sleep(sleep_time)
                    else:
                        self.logger.error(f"Failed to process batch {batch_idx + 1} after {max_retries} attempts")
        
        data = self.get_data_as_dict(extracted_data_list)
        data_dataframe=pd.DataFrame(data)
        data_dataframe.to_csv("./CVs_data.csv",index=False)
        return data_dataframe

    def run(self, path: str, output_path: Optional[str] = None) -> pd.DataFrame:
        """Main method to run the extraction process."""
        self.logger.info(f"Starting CV extraction from {path}")
        
        # Get PDF contents
        pdfs_list = self.get_pdfs_content(path)
        
        if not pdfs_list or len(pdfs_list) == 0:
            self.logger.warning("No PDF content was found or extracted")
            return pd.DataFrame()
        
        # Generate structured data
        self.logger.info(f"Generating structured data from {len(pdfs_list)} CVs")
        df = self.generate_data(pdfs_list)
        
        # Save to CSV if output path is provided
        if output_path and not df.empty:
            self.logger.info(f"Saving extracted data to {output_path}")
            df.to_csv(output_path, index=False)
        
        return df
