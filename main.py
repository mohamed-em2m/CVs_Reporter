from init_agent import ExtractAgent
from pdf_build import create_survey_report
import os
import logging

if __name__ == "__main__":
    import argparse
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Process CVs from a directory")
    parser.add_argument("path", help="Path to directory containing PDF files")
    parser.add_argument("--output", help="Output PDF report file path", default="csv_report.pdf")
    parser.add_argument("--output_csv", help="Output CSV file path", default="candidate_data.csv")
    parser.add_argument("--key", required=True, help="Gemini API key")
    parser.add_argument("--model", help="Model name", default="gemini-2.0-flash")
    parser.add_argument("--save_csv", action="store_true", help="Save data to CSV file", default=True)
    
    args = parser.parse_args()
    print(args)
    # Set environment variables
    os.environ['MODEL'] = args.model
    os.environ["GEMINI_API_KEY"] = args.key
    
    # Initialize and run the extraction agent
    logger.info(f"Initializing extraction agent with model: {args.model}")
    agent = ExtractAgent()
    
    logger.info(f"Processing CVs from directory: {args.path}")
    data = agent.run(args.path)  # Fixed: should pass the path, not the API key
    
    # Create the PDF report
    logger.info(f"Creating survey report: {args.output}")
    create_survey_report(data, args.output)
    
    # Save CSV if requested
    if args.save_csv:  # Fixed: using the correct argument name
        logger.info(f"Saving data to CSV: {args.output_csv}")
        data.to_csv(args.output_csv, index=False)
        print("Data saved to CSV successfully")