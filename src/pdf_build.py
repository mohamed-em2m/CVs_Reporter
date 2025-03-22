import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage, ListFlowable, ListItem, PageBreak
from reportlab.lib.units import inch
from PIL import Image as PILImage, ImageDraw, ImageFont
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import random
import plotly.io as pio
import ast
pio.kaleido.scope.chromium_args = tuple([arg for arg in pio.kaleido.scope.chromium_args if arg != "--disable-dev-shm-usage"])
#pio.kaleido.scope.chromium_args = tuple([arg for arg in pio.kaleido.scope.chromium_args if arg != "--disable-dev-shm-usage"])
class NotionDataPDF:
    def __init__(self, output_filename, title="Data Visualization Report", pagesize=A4):
        """Initialize PDF document with Notion-like styling"""
        self.output_filename = output_filename
        self.title = title
        self.document = SimpleDocTemplate(
            output_filename,
            pagesize=pagesize,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        # Create custom styles similar to Notion
        self.styles = getSampleStyleSheet()
        
        # Customize title style
        self.styles.add(ParagraphStyle(
            name='NotionTitle',
            fontName='Helvetica-Bold',
            fontSize=24,
            spaceAfter=16,
            textColor=colors.black
        ))
        
        # Customize heading styles
        self.styles.add(ParagraphStyle(
            name='NotionH1',
            fontName='Helvetica-Bold',
            fontSize=20,
            spaceAfter=12,
            spaceBefore=24,
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='NotionH2',
            fontName='Helvetica-Bold',
            fontSize=16,
            spaceAfter=10,
            spaceBefore=16,
            textColor=colors.black
        ))
        
        # Normal text
        self.styles.add(ParagraphStyle(
            name='NotionText',
            fontName='Helvetica',
            fontSize=11,
            spaceAfter=12,
            leading=14,
            textColor=colors.black
        ))
        
        # Initialize content elements list
        self.elements = []
        
        # Create directory for chart images
        self.img_dir = "chart_images"
        os.makedirs(self.img_dir, exist_ok=True)
    
    def add_heading(self, text, level=1):
        """Add a heading with specified level (1-2)"""
        if level == 1:
            self.elements.append(Paragraph(text, self.styles['NotionH1']))
        else:
            self.elements.append(Paragraph(text, self.styles['NotionH2']))
    
    def add_paragraph(self, text):
        """Add a regular paragraph of text"""
        self.elements.append(Paragraph(text, self.styles['NotionText']))
    
    def add_spacer(self, height=0.1):
        """Add vertical space in inches"""
        self.elements.append(Spacer(1, height*inch))
    
    def add_page_break(self):
        """Add a page break"""
        self.elements.append(PageBreak())
    
    def add_plotly_figure(self, fig, width=6.5, height=4, dpi=300, caption=None):
        """Add a Plotly figure to the PDF"""
        # Generate unique filename for the image
        img_count = len([f for f in os.listdir(self.img_dir) if f.endswith('.png')])
        img_path = os.path.join(self.img_dir, f"chart_{img_count}.png")
        
        # Save the figure as an image
        fig.write_image(img_path, width=width*dpi, height=height*dpi)
        
        # Add the image to the PDF
        img = ReportLabImage(img_path, width=width*inch, height=height*inch)
        self.elements.append(img)
        
        # Add caption if provided
        if caption:
            caption_style = ParagraphStyle(
                name='Caption',
                parent=self.styles['NotionText'],
                fontSize=9,
                alignment=1  # Center alignment
            )
            self.elements.append(Paragraph(caption, caption_style))
        
        self.elements.append(Spacer(1, 0.2*inch))
        
        return img_path
    
    def add_table_from_dataframe(self, df, max_rows=10, include_index=False, colWidths=None):
        """Add a table from a pandas DataFrame"""
        # Prepare data for the table
        if include_index:
            headers = ['Index'] + list(df.columns)
            data = [[str(i)] + [str(x) for x in row] for i, row in zip(df.index[:max_rows], df.values[:max_rows])]
        else:
            headers = list(df.columns)
            data = [[str(x) for x in row] for row in df.values[:max_rows]]
        
        # Add headers to data
        table_data = [headers] + data
        
        # Create the table
        if colWidths is None:
            # Calculate usable width
            usable_width = self.document.width
            colWidths = [usable_width / len(headers)] * len(headers)
        
        table = Table(table_data, colWidths=colWidths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        
        self.elements.append(table)
        
        # Add a note if the dataframe was truncated
        if len(df) > max_rows:
            self.elements.append(Paragraph(f"Note: Showing {max_rows} rows out of {len(df)} total rows.", 
                                         self.styles['NotionText']))
        
        self.elements.append(Spacer(1, 0.2*inch))
    
    def create_title_page(self, title_text, subtitle_text=None, date_range=None):
        """Create a separate title page at the BEGINNING of the document"""
        # Create a new document just for the title page
        title_doc = SimpleDocTemplate(
            "title_page.pdf",
            pagesize=self.document.pagesize,
            rightMargin=self.document.rightMargin,
            leftMargin=self.document.leftMargin,
            topMargin=self.document.topMargin,
            bottomMargin=self.document.bottomMargin
        )
        
        title_elements = []
        
        # Add spacer to push content to middle
        title_elements.append(Spacer(1, 2*inch))
        
        # Add main title with larger font
        title_style = ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['NotionTitle'],
            fontSize=36,
            alignment=1  # Center alignment
        )
        title_elements.append(Paragraph(title_text, title_style))
        
        # Add subtitle if provided
        if subtitle_text:
            subtitle_style = ParagraphStyle(
                name='CoverSubtitle',
                parent=self.styles['NotionH1'],
                fontSize=18,
                alignment=1,  # Center alignment
                spaceAfter=36
            )
            title_elements.append(Spacer(1, 0.5*inch))
            title_elements.append(Paragraph(subtitle_text, subtitle_style))
        
        # Add date range if provided
        if date_range:
            date_style = ParagraphStyle(
                name='CoverDate',
                parent=self.styles['NotionText'],
                fontSize=14,
                alignment=1  # Center alignment
            )
            title_elements.append(Spacer(1, 0.5*inch))
            title_elements.append(Paragraph(f"Study Period: {date_range}", date_style))
        
        # Build the title page
        title_doc.build(title_elements)
        
        # Now add this at the beginning of our document
        self.elements.insert(0, PageBreak())
        
        # Add title to main document as well (after page break)
        self.elements.insert(0, Paragraph(self.title, self.styles['NotionTitle']))
    
    def build(self):
        """Build and save the PDF document"""
        self.document.build(self.elements)
        return self.output_filename

def create_survey_report(df, output_pdf="survey_report.pdf"):
    """Create a comprehensive survey report PDF with visualizations"""
    # Initialize the PDF
    report = NotionDataPDF(output_pdf, "Survey Analysis Report")
    #date_range = f"{start_date} to {end_date}" if start_date and end_date else None
    report.create_title_page("CVS Survey Analysis", "Comprehensive Results")
    report.add_spacer()
    # Add report overview
#    report.add_heading("Report Overview", 1)
#    report.add_paragraph(f"{report.get_summary(df)}")
#    
    
    # Display sample of the dat
    loop=0
    # Loop through each column and create a histogram
    for index, column in enumerate(df.columns):
        # Add a page break before each new section (except the first one)

            
        report.add_heading(f"{column} Distribution", 1)
        report.add_paragraph(f"The chart below shows the distribution of responses across {column}:")
        #report.add_spacer()
        print(df[column].iloc[-1],column,type(df[column].iloc[-1]) ,type (df[column].iloc[-1]) is str  )
        if pd.api.types.is_numeric_dtype(df[column]) or (
            isinstance(df[column].iloc[-1], str) and not df[column].iloc[-1].startswith("[")
        ):            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=df[column], 
                marker_color='blue', 
                opacity=0.7
            ))
            fig.update_layout(
                title=f"{column} Distribution",
                xaxis_title=f"{column}",
                yaxis_title="Number of Responses",
                bargap=.9,
                width=2400,    # Increase the width of the figure
                height=2400,font=dict(size=18)      # Increase the height of the figure
            )
            fig.update_xaxes(tickmode='linear', dtick=1,    showticklabels=True)
            report.add_plotly_figure(fig, width=7.5, height=3.5, caption=f"Figure {index+1}: Distribution of responses by {column}")
            loop+=1
            if loop%2==0:
                report.add_page_break()
        else:
            if (loop%2!=0):
               report.add_page_break()

                
            # Handle skills column with ast.literal_eval
            skills_counts = {}
            try:
                for skills in  df["skills"]:
                    for skill in  ast.literal_eval(skills):
                        if len(skill)>25:
                            skill=skill[:25]
                        skills_counts[skill] = skills_counts.get(skill, 0) + 1
                sorted_skills=sorted(list(skills_counts.items()), key=lambda x: x[1], reverse=True)
                max_indexs=80
                sorted_skills_keys=[ i[0] for i in sorted_skills][:max_indexs]
                sorted_skills_values=[ i[1] for i in sorted_skills][:max_indexs]

                skills =sorted_skills_keys
                counts = sorted_skills_values

                # Generate a random color for each skill
                colors = [f'rgb({random.randint(50, 200)},{random.randint(50, 200)},{random.randint(50, 200)})' for _ in skills]
                print
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=counts,
                    y=skills,
                    orientation="h",  # Horizontal bars
                    marker=dict(color=colors)  # Assign colors
                ))

                fig.update_layout(
                    title=f"{column} Distribution",
                    xaxis_title="Number of Responses",
                    yaxis_title=f"{column}",
                    bargap=.55,
                    width=2400,    # Increase the width
                    height=2500,   # Increase the height
                    font=dict(size=20),
                    showlegend=False
                )

                fig.update_xaxes(tickmode='linear', dtick=1, showticklabels=True)
                
                report.add_plotly_figure(fig, width=7.5, height=10, caption=f"Figure {index+1}: Distribution of responses by {column}")
            except Exception as e:
                print(e)
                report.add_paragraph(f"{e}")
                continue
                
        # Add the figure to the PDF

            
    # Create the title page (should be done last to appear first)
    #date_range = f"{start_date} to {end_date}" if start_date and end_date else None
    #report.create_title_page("CVS Survey Analysis", "Comprehensive Results", date_range)
    
    # Build the PDF
    report.build()
    print(f"PDF report saved as: {output_pdf}")
    return output_pdf