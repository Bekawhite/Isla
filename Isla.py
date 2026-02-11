import os
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import warnings
import time
from typing import Optional, List, Dict, Tuple
import gc
warnings.filterwarnings('ignore')

# Try multiple PDF libraries for robustness
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("pdfplumber not installed, using alternative methods")

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    print("camelot not installed, using alternative methods")

try:
    from tabula import read_pdf
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    print("tabula not installed, using alternative methods")

class HighVolumePDFtoExcelConverter:
    """
    High-performance PDF to Excel converter optimized for large datasets (1000+ rows)
    """
    
    def __init__(self, max_workers: int = 4, chunk_size: int = 1000):
        """
        Initialize the converter
        
        Args:
            max_workers: Number of parallel workers for processing
            chunk_size: Rows to process in each chunk (for memory optimization)
        """
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.output_dir = "converted_excel_large"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Performance metrics
        self.metrics = {
            'total_rows': 0,
            'processing_time': 0,
            'tables_found': 0,
            'memory_usage_mb': 0
        }
    
    def convert_large_pdf_to_excel(self,
                                  pdf_path: str,
                                  excel_path: Optional[str] = None,
                                  max_rows: Optional[int] = None,
                                  max_columns: Optional[int] = None,
                                  extraction_method: str = 'auto',
                                  optimize_memory: bool = True,
                                  split_by_pages: bool = False) -> str:
        """
        Convert large PDF files to Excel with high performance
        
        Args:
            pdf_path: Path to PDF file
            excel_path: Output Excel file path
            max_rows: Maximum rows to extract (None for unlimited)
            max_columns: Maximum columns to extract
            extraction_method: 'auto', 'camelot', 'pdfplumber', 'tabula', 'hybrid'
            optimize_memory: Use memory-efficient processing
            split_by_pages: Split large PDFs into multiple Excel files by pages
        
        Returns:
            Path to created Excel file(s)
        """
        
        print(f"🔍 Starting conversion of: {pdf_path}")
        print(f"📊 Method: {extraction_method}")
        start_time = time.time()
        
        # Validate PDF file
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Generate output path if not provided
        if excel_path is None:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            timestamp = int(time.time())
            excel_path = os.path.join(self.output_dir, f"{base_name}_{timestamp}.xlsx")
        
        # Get PDF page count
        page_count = self._get_pdf_page_count(pdf_path)
        print(f"📄 PDF has {page_count} pages")
        
        # Choose extraction method
        if extraction_method == 'auto':
            # Auto-detect best method based on PDF characteristics
            extraction_method = self._detect_best_method(pdf_path)
            print(f"🤖 Auto-selected method: {extraction_method}")
        
        # Process based on size
        if page_count > 50 and split_by_pages:
            # For very large PDFs, split by pages
            print(f"📚 Large PDF detected ({page_count} pages). Splitting by pages...")
            return self._process_large_pdf_by_pages(
                pdf_path, excel_path, max_rows, max_columns, 
                extraction_method, optimize_memory
            )
        else:
            # Process as single file
            return self._process_pdf(
                pdf_path, excel_path, max_rows, max_columns, 
                extraction_method, optimize_memory
            )
    
    def _process_pdf(self, pdf_path: str, excel_path: str, 
                    max_rows: Optional[int], max_columns: Optional[int],
                    method: str, optimize_memory: bool) -> str:
        """Process PDF file with selected method"""
        
        try:
            if method == 'camelot' and CAMELOT_AVAILABLE:
                result = self._extract_with_camelot(pdf_path, optimize_memory)
            elif method == 'pdfplumber' and PDFPLUMBER_AVAILABLE:
                result = self._extract_with_pdfplumber(pdf_path, optimize_memory)
            elif method == 'tabula' and TABULA_AVAILABLE:
                result = self._extract_with_tabula(pdf_path, optimize_memory)
            elif method == 'hybrid':
                result = self._extract_with_hybrid(pdf_path, optimize_memory)
            else:
                # Fallback to available method
                if PDFPLUMBER_AVAILABLE:
                    result = self._extract_with_pdfplumber(pdf_path, optimize_memory)
                elif CAMELOT_AVAILABLE:
                    result = self._extract_with_camelot(pdf_path, optimize_memory)
                elif TABULA_AVAILABLE:
                    result = self._extract_with_tabula(pdf_path, optimize_memory)
                else:
                    raise ImportError("No PDF extraction library available")
            
            # Apply row and column limits
            result = self._apply_limits_to_data(result, max_rows, max_columns)
            
            # Save to Excel
            self._save_to_excel(result, excel_path, optimize_memory)
            
            # Update metrics
            self.metrics['processing_time'] = time.time() - start_time
            self.metrics['total_rows'] = sum(len(df) for df in result.values())
            self.metrics['tables_found'] = len(result)
            
            print(f"✅ Conversion completed successfully!")
            print(f"📈 Statistics:")
            print(f"   • Total rows extracted: {self.metrics['total_rows']:,}")
            print(f"   • Tables found: {self.metrics['tables_found']}")
            print(f"   • Processing time: {self.metrics['processing_time']:.2f} seconds")
            print(f"   • Output file: {excel_path}")
            
            return excel_path
            
        except Exception as e:
            print(f"❌ Error during conversion: {str(e)}")
            # Try fallback method
            print("🔄 Trying fallback method...")
            return self._fallback_conversion(pdf_path, excel_path, max_rows, max_columns)
    
    def _extract_with_camelot(self, pdf_path: str, optimize_memory: bool) -> Dict[str, pd.DataFrame]:
        """Extract tables using Camelot (best for structured tables)"""
        print("🔄 Using Camelot for table extraction...")
        
        try:
            # Read all tables from PDF
            tables = camelot.read_pdf(pdf_path, 
                                     pages='all',
                                     flavor='lattice',
                                     suppress_stdout=True,
                                     strip_text='\n')
            
            print(f"📊 Camelot found {len(tables)} potential tables")
            
            result = {}
            for i, table in enumerate(tables):
                if table.parsing_report['accuracy'] > 50:  # Filter low accuracy tables
                    df = table.df
                    
                    # Clean the dataframe
                    df = self._clean_dataframe(df)
                    
                    if not df.empty and len(df) > 1:
                        table_name = f"Table_{i+1}"
                        if optimize_memory:
                            df = self._optimize_dataframe_memory(df)
                        result[table_name] = df
            
            return result
            
        except Exception as e:
            print(f"Camelot extraction failed: {e}")
            return {}
    
    def _extract_with_pdfplumber(self, pdf_path: str, optimize_memory: bool) -> Dict[str, pd.DataFrame]:
        """Extract tables using PDFPlumber"""
        print("🔄 Using PDFPlumber for extraction...")
        
        result = {}
        table_counter = 1
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            
            # Process pages in parallel for large PDFs
            if total_pages > 10 and self.max_workers > 1:
                print(f"⚡ Processing {total_pages} pages in parallel...")
                with ThreadPoolExecutor(max_workers=min(self.max_workers, total_pages)) as executor:
                    page_results = list(executor.map(
                        self._process_pdfplumber_page,
                        [(pdf_path, i) for i in range(total_pages)]
                    ))
                
                # Combine results
                for page_tables in page_results:
                    for df in page_tables:
                        if not df.empty:
                            table_name = f"Table_{table_counter}"
                            if optimize_memory:
                                df = self._optimize_dataframe_memory(df)
                            result[table_name] = df
                            table_counter += 1
            else:
                # Process pages sequentially
                for page_num, page in enumerate(pdf.pages):
                    print(f"📖 Processing page {page_num + 1}/{total_pages}")
                    
                    # Extract tables
                    tables = page.extract_tables()
                    
                    for table_num, table_data in enumerate(tables):
                        if table_data:
                            df = pd.DataFrame(table_data)
                            df = self._clean_dataframe(df)
                            
                            if not df.empty and len(df) > 1:
                                table_name = f"Page_{page_num+1}_Table_{table_num+1}"
                                if optimize_memory:
                                    df = self._optimize_dataframe_memory(df)
                                result[table_name] = df
                    
                    # Extract text if no tables found
                    if not tables:
                        text = page.extract_text()
                        if text and len(text.strip()) > 0:
                            df = self._text_to_dataframe(text)
                            if not df.empty:
                                table_name = f"Page_{page_num+1}_Text"
                                result[table_name] = df
        
        return result
    
    def _process_pdfplumber_page(self, args: Tuple) -> List[pd.DataFrame]:
        """Process a single page with PDFPlumber (for parallel processing)"""
        pdf_path, page_num = args
        page_tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    tables = page.extract_tables()
                    
                    for table_data in tables:
                        if table_data:
                            df = pd.DataFrame(table_data)
                            df = self._clean_dataframe(df)
                            if not df.empty and len(df) > 1:
                                page_tables.append(df)
        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
        
        return page_tables
    
    def _extract_with_tabula(self, pdf_path: str, optimize_memory: bool) -> Dict[str, pd.DataFrame]:
        """Extract tables using Tabula"""
        print("🔄 Using Tabula for extraction...")
        
        try:
            # Read all tables
            dfs = read_pdf(pdf_path, pages='all', multiple_tables=True)
            
            result = {}
            for i, df in enumerate(dfs):
                if not df.empty:
                    df = self._clean_dataframe(df)
                    if optimize_memory:
                        df = self._optimize_dataframe_memory(df)
                    result[f"Table_{i+1}"] = df
            
            return result
            
        except Exception as e:
            print(f"Tabula extraction failed: {e}")
            return {}
    
    def _extract_with_hybrid(self, pdf_path: str, optimize_memory: bool) -> Dict[str, pd.DataFrame]:
        """Use multiple methods and combine best results"""
        print("🔄 Using hybrid extraction method...")
        
        all_results = {}
        
        # Try Camelot first
        if CAMELOT_AVAILABLE:
            camelot_results = self._extract_with_camelot(pdf_path, optimize_memory)
            all_results.update(camelot_results)
        
        # Try PDFPlumber for remaining pages
        if PDFPLUMBER_AVAILABLE and len(all_results) < 5:  # If few tables found
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                processed_pages = set()
                
                # Identify which pages were processed by Camelot
                for table_name in all_results.keys():
                    if 'Page_' in table_name:
                        try:
                            page_num = int(table_name.split('_')[1])
                            processed_pages.add(page_num)
                        except:
                            pass
                
                # Process remaining pages with PDFPlumber
                for page_num in range(total_pages):
                    if page_num not in processed_pages:
                        page = pdf.pages[page_num]
                        tables = page.extract_tables()
                        
                        for table_num, table_data in enumerate(tables):
                            if table_data:
                                df = pd.DataFrame(table_data)
                                df = self._clean_dataframe(df)
                                if not df.empty:
                                    table_name = f"Page_{page_num+1}_Table_{table_num+1}"
                                    if optimize_memory:
                                        df = self._optimize_dataframe_memory(df)
                                    all_results[table_name] = df
        
        return all_results
    
    def _process_large_pdf_by_pages(self, pdf_path: str, base_excel_path: str,
                                   max_rows: Optional[int], max_columns: Optional[int],
                                   method: str, optimize_memory: bool) -> str:
        """Process very large PDFs by splitting into multiple Excel files"""
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            pages_per_file = min(50, total_pages)  # Max 50 pages per file
        
        # Create a directory for split files
        base_name = os.path.splitext(os.path.basename(base_excel_path))[0]
        split_dir = os.path.join(self.output_dir, f"{base_name}_split")
        os.makedirs(split_dir, exist_ok=True)
        
        file_paths = []
        
        for start_page in range(0, total_pages, pages_per_file):
            end_page = min(start_page + pages_per_file, total_pages)
            chunk_pdf_path = self._extract_pdf_pages(pdf_path, start_page, end_page, split_dir)
            
            if chunk_pdf_path:
                chunk_excel_path = os.path.join(
                    split_dir, 
                    f"{base_name}_pages_{start_page+1}_{end_page}.xlsx"
                )
                
                try:
                    result_path = self._process_pdf(
                        chunk_pdf_path, chunk_excel_path, max_rows, max_columns,
                        method, optimize_memory
                    )
                    file_paths.append(result_path)
                    
                    # Clean up temporary PDF chunk
                    os.remove(chunk_pdf_path)
                    
                except Exception as e:
                    print(f"Error processing pages {start_page+1}-{end_page}: {e}")
        
        # Create a master file with links to all split files
        master_path = self._create_master_file(file_paths, base_excel_path)
        
        print(f"📚 Large PDF processed as {len(file_paths)} separate files")
        print(f"📋 Master file created: {master_path}")
        
        return master_path
    
    def _extract_pdf_pages(self, pdf_path: str, start_page: int, 
                          end_page: int, output_dir: str) -> Optional[str]:
        """Extract specific pages from PDF"""
        try:
            from PyPDF2 import PdfReader, PdfWriter
            
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            for page_num in range(start_page, end_page):
                if page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])
            
            output_path = os.path.join(output_dir, f"temp_pages_{start_page+1}_{end_page}.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            print(f"Error extracting pages: {e}")
            return None
    
    def _create_master_file(self, file_paths: List[str], master_path: str) -> str:
        """Create a master Excel file with summary and links"""
        
        summary_data = []
        for i, file_path in enumerate(file_paths):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            # Try to get row count from each file
            try:
                xl = pd.ExcelFile(file_path)
                total_rows = 0
                for sheet in xl.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet, nrows=1)
                    # Get approximate row count from file size and columns
                    total_rows += len(pd.read_excel(file_path, sheet_name=sheet))
            except:
                total_rows = "Unknown"
            
            summary_data.append({
                'File': file_name,
                'Size_MB': f"{file_size:.2f}",
                'Rows': total_rows,
                'Path': file_path
            })
        
        # Create summary dataframe
        summary_df = pd.DataFrame(summary_data)
        
        # Save master file
        with pd.ExcelWriter(master_path, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Add instructions sheet
            instructions = pd.DataFrame({
                'Instruction': [
                    'This is a master file for large PDF conversion',
                    f'Total split files: {len(file_paths)}',
                    'Open individual files for detailed data',
                    'The Summary sheet contains file locations and statistics'
                ]
            })
            instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
        return master_path
    
    def _apply_limits_to_data(self, data: Dict[str, pd.DataFrame], 
                             max_rows: Optional[int], max_columns: Optional[int]) -> Dict[str, pd.DataFrame]:
        """Apply row and column limits to data"""
        
        if max_rows is None and max_columns is None:
            return data
        
        result = {}
        for name, df in data.items():
            # Apply column limit
            if max_columns and len(df.columns) > max_columns:
                df = df.iloc[:, :max_columns]
            
            # Apply row limit
            if max_rows and len(df) > max_rows:
                df = df.head(max_rows)
            
            result[name] = df
        
        return result
    
    def _save_to_excel(self, data: Dict[str, pd.DataFrame], 
                      excel_path: str, optimize_memory: bool):
        """Save data to Excel with memory optimization"""
        
        print(f"💾 Saving to Excel: {excel_path}")
        
        if optimize_memory and len(data) > 1:
            # Use chunked writing for large datasets
            self._save_to_excel_chunked(data, excel_path)
        else:
            # Standard writing
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                for sheet_name, df in data.items():
                    # Truncate sheet name if too long
                    safe_sheet_name = str(sheet_name)[:31]
                    
                    # Write dataframe to Excel
                    df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                    
                    # Auto-adjust column widths
                    worksheet = writer.sheets[safe_sheet_name]
                    for idx, col in enumerate(df.columns):
                        column_width = max(
                            df[col].astype(str).str.len().max(),
                            len(str(col))
                        ) + 2
                        column_letter = chr(65 + idx) if idx < 26 else f"A{chr(65 + idx - 26)}"
                        worksheet.column_dimensions[column_letter].width = min(column_width, 50)
    
    def _save_to_excel_chunked(self, data: Dict[str, pd.DataFrame], excel_path: str):
        """Save large datasets in chunks to conserve memory"""
        
        print("⚡ Using chunked writing for memory optimization...")
        
        # Create writer
        writer = pd.ExcelWriter(excel_path, engine='openpyxl')
        
        for sheet_name, df in data.items():
            safe_sheet_name = str(sheet_name)[:31]
            
            if len(df) > self.chunk_size:
                # Write in chunks
                chunks = [df[i:i + self.chunk_size] for i in range(0, len(df), self.chunk_size)]
                
                # Write first chunk with header
                chunks[0].to_excel(writer, sheet_name=safe_sheet_name, index=False)
                
                # Append remaining chunks
                for chunk in chunks[1:]:
                    chunk.to_excel(writer, sheet_name=safe_sheet_name, 
                                 startrow=writer.sheets[safe_sheet_name].max_row,
                                 index=False, header=False)
                    
                    # Force garbage collection
                    if len(chunk) > 1000:
                        gc.collect()
            else:
                # Write entire dataframe
                df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
        
        writer.save()
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and optimize dataframe"""
        
        if df.empty:
            return df
        
        # Remove completely empty rows and columns
        df = df.replace(r'^\s*$', pd.NA, regex=True)
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Check if first row should be headers
        if len(df) > 1:
            first_row = df.iloc[0]
            # Heuristic: if first row has many unique values and isn't too long
            unique_count = first_row.astype(str).apply(lambda x: x.strip()).nunique()
            if unique_count > len(df.columns) / 3 and first_row.astype(str).str.len().max() < 100:
                df.columns = [str(col).strip() for col in first_row]
                df = df.iloc[1:].reset_index(drop=True)
        
        # Strip whitespace from all string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        
        return df
    
    def _optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize dataframe memory usage"""
        
        # Convert object columns to categorical if they have few unique values
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.5:  # If less than 50% unique values
                    df[col] = df[col].astype('category')
        
        # Downcast numeric columns
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Downcast integers
            if df[col].dtype in ['int64', 'int32']:
                df[col] = pd.to_numeric(df[col], downcast='integer')
            
            # Downcast floats
            elif df[col].dtype in ['float64', 'float32']:
                df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    
    def _text_to_dataframe(self, text: str) -> pd.DataFrame:
        """Convert text to dataframe"""
        
        lines = text.strip().split('\n')
        rows = []
        
        for line in lines:
            if line.strip():
                # Split by common delimiters
                for delimiter in ['\t', '|', ',', ';', '  ']:
                    parts = [p.strip() for p in line.split(delimiter) if p.strip()]
                    if len(parts) > 1:
                        rows.append(parts)
                        break
                else:
                    # No delimiter found, treat as single column
                    rows.append([line.strip()])
        
        if rows:
            # Create dataframe
            max_cols = max(len(row) for row in rows)
            for i in range(len(rows)):
                rows[i].extend([''] * (max_cols - len(rows[i])))
            
            return pd.DataFrame(rows)
        
        return pd.DataFrame()
    
    def _get_pdf_page_count(self, pdf_path: str) -> int:
        """Get number of pages in PDF"""
        try:
            if PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(pdf_path) as pdf:
                    return len(pdf.pages)
            else:
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                return len(reader.pages)
        except:
            return 0
    
    def _detect_best_method(self, pdf_path: str) -> str:
        """Auto-detect best extraction method based on PDF characteristics"""
        
        try:
            # Quick analysis of first few pages
            with pdfplumber.open(pdf_path) as pdf:
                sample_pages = min(3, len(pdf.pages))
                has_tables = False
                
                for i in range(sample_pages):
                    page = pdf.pages[i]
                    tables = page.extract_tables()
                    if tables and any(len(t) > 1 for t in tables):
                        has_tables = True
                        break
            
            if has_tables and CAMELOT_AVAILABLE:
                return 'camelot'
            elif PDFPLUMBER_AVAILABLE:
                return 'pdfplumber'
            elif TABULA_AVAILABLE:
                return 'tabula'
            else:
                return 'hybrid'
                
        except:
            return 'pdfplumber' if PDFPLUMBER_AVAILABLE else 'tabula'
    
    def _fallback_conversion(self, pdf_path: str, excel_path: str,
                            max_rows: Optional[int], max_columns: Optional[int]) -> str:
        """Fallback conversion method when primary methods fail"""
        
        print("🔄 Using fallback OCR-based extraction...")
        
        try:
            # Try OCR as last resort
            try:
                import pytesseract
                from PIL import Image
                from pdf2image import convert_from_path
                
                print("📷 Converting PDF to images for OCR...")
                
                # Convert PDF to images
                images = convert_from_path(pdf_path, dpi=200)
                
                all_text = []
                for i, image in enumerate(images[:10]):  # Limit to first 10 pages
                    print(f"🔍 OCR processing page {i+1}/{len(images)}")
                    text = pytesseract.image_to_string(image)
                    all_text.append(text)
                
                # Combine all text
                combined_text = '\n'.join(all_text)
                
                # Convert to dataframe
                df = self._text_to_dataframe(combined_text)
                
                if not df.empty:
                    # Apply limits
                    if max_rows and len(df) > max_rows:
                        df = df.head(max_rows)
                    if max_columns and len(df.columns) > max_columns:
                        df = df.iloc[:, :max_columns]
                    
                    # Save to Excel
                    df.to_excel(excel_path, index=False, sheet_name='OCR_Extracted')
                    
                    print(f"✅ OCR extraction completed: {excel_path}")
                    return excel_path
                    
            except ImportError:
                print("OCR libraries not available")
            
            # Ultimate fallback: extract raw text
            print("📝 Extracting raw text...")
            
            if PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(pdf_path) as pdf:
                    all_text = []
                    for page in pdf.pages[:20]:  # Limit to first 20 pages
                        text = page.extract_text()
                        if text:
                            all_text.append(text)
                
                combined_text = '\n'.join(all_text)
                lines = combined_text.split('\n')
                
                # Create simple dataframe
                data = {'Text': lines}
                if max_rows:
                    data['Text'] = data['Text'][:max_rows]
                
                df = pd.DataFrame(data)
                
                if max_columns and len(df.columns) > max_columns:
                    df = df.iloc[:, :max_columns]
                
                df.to_excel(excel_path, index=False, sheet_name='Text_Extracted')
                
                print(f"✅ Text extraction completed: {excel_path}")
                return excel_path
                
        except Exception as e:
            print(f"❌ Fallback conversion failed: {e}")
            raise
    
    def get_conversion_report(self) -> Dict:
        """Get detailed conversion report"""
        return {
            'total_rows': self.metrics['total_rows'],
            'processing_time_seconds': self.metrics['processing_time'],
            'tables_found': self.metrics['tables_found'],
            'rows_per_second': self.metrics['total_rows'] / max(self.metrics['processing_time'], 0.001),
            'status': 'success' if self.metrics['total_rows'] > 0 else 'partial'
        }

# ============================================================================
# SIMPLIFIED USER INTERFACE
# ============================================================================

def run_batch_conversion():
    """Convert multiple PDF files at once"""
    converter = HighVolumePDFtoExcelConverter(max_workers=8)
    
    print("=" * 60)
    print("HIGH-VOLUME PDF TO EXCEL CONVERTER")
    print("=" * 60)
    print("This converter is optimized for large PDFs (1000+ rows)")
    print()
    
    # Get input
    pdf_folder = input("Enter folder containing PDF files (or single file path): ").strip()
    
    if os.path.isdir(pdf_folder):
        # Process all PDFs in folder
        pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
        print(f"Found {len(pdf_files)} PDF files")
        
        max_rows = input("Max rows per sheet (Enter for unlimited): ").strip()
        max_rows = int(max_rows) if max_rows.isdigit() else None
        
        max_cols = input("Max columns per sheet (Enter for unlimited): ").strip()
        max_cols = int(max_cols) if max_cols.isdigit() else None
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_folder, pdf_file)
            print(f"\n📂 Processing: {pdf_file}")
            
            try:
                result = converter.convert_large_pdf_to_excel(
                    pdf_path,
                    max_rows=max_rows,
                    max_columns=max_cols,
                    extraction_method='auto',
                    optimize_memory=True,
                    split_by_pages=True  # Auto-split large files
                )
                print(f"✅ Saved to: {result}")
            except Exception as e:
                print(f"❌ Failed: {e}")
    
    else:
        # Process single file
        pdf_path = pdf_folder
        
        if not os.path.exists(pdf_path):
            print("File not found!")
            return
        
        # Get configuration
        max_rows = input("Max rows per sheet (Enter for unlimited): ").strip()
        max_rows = int(max_rows) if max_rows.isdigit() else None
        
        max_cols = input("Max columns per sheet (Enter for unlimited): ").strip()
        max_cols = int(max_cols) if max_cols.isdigit() else None
        
        method = input("Extraction method (auto/camelot/pdfplumber/tabula/hybrid) [auto]: ").strip().lower()
        if method not in ['auto', 'camelot', 'pdfplumber', 'tabula', 'hybrid']:
            method = 'auto'
        
        optimize = input("Optimize memory usage? (y/n) [y]: ").strip().lower()
        optimize = optimize != 'n'
        
        split = input("Auto-split large PDFs? (y/n) [y]: ").strip().lower()
        split = split != 'n'
        
        print(f"\n{'='*60}")
        print("Starting conversion...")
        print(f"File: {pdf_path}")
        print(f"Max rows: {max_rows or 'Unlimited'}")
        print(f"Max columns: {max_cols or 'Unlimited'}")
        print(f"Method: {method}")
        print(f"Memory optimization: {'Yes' if optimize else 'No'}")
        print(f"Auto-split: {'Yes' if split else 'No'}")
        print(f"{'='*60}\n")
        
        try:
            result = converter.convert_large_pdf_to_excel(
                pdf_path,
                max_rows=max_rows,
                max_columns=max_cols,
                extraction_method=method,
                optimize_memory=optimize,
                split_by_pages=split
            )
            
            print(f"\n{'='*60}")
            print("✅ CONVERSION COMPLETE!")
            print(f"{'='*60}")
            
            # Show report
            report = converter.get_conversion_report()
            for key, value in report.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            
            print(f"\nOutput file: {result}")
            
            # Ask to open file
            open_file = input("\nOpen output file? (y/n): ").strip().lower()
            if open_file == 'y':
                import subprocess
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(result)
                    elif os.name == 'posix':  # macOS, Linux
                        subprocess.call(['open', result] if sys.platform == 'darwin' else ['xdg-open', result])
                except:
                    print("Could not open file automatically")
            
        except Exception as e:
            print(f"\n❌ CONVERSION FAILED: {e}")
            import traceback
            traceback.print_exc()

# ============================================================================
# QUICK START FUNCTION
# ============================================================================

def quick_convert(pdf_path: str, output_path: Optional[str] = None, 
                 max_rows: Optional[int] = None, max_columns: Optional[int] = None):
    """
    Quick conversion function for simple use cases
    
    Example:
        quick_convert("large_report.pdf", max_rows=5000, max_columns=20)
    """
    converter = HighVolumePDFtoExcelConverter()
    return converter.convert_large_pdf_to_excel(
        pdf_path,
        excel_path=output_path,
        max_rows=max_rows,
        max_columns=max_columns,
        extraction_method='auto',
        optimize_memory=True,
        split_by_pages=True
    )

# ============================================================================
# INSTALLATION SCRIPT
# ============================================================================

def install_dependencies():
    """Install all required dependencies"""
    
    requirements = [
        "pandas>=1.5.0",
        "openpyxl>=3.0.0",
        "pdfplumber>=0.8.0",
        "PyPDF2>=3.0.0",
        "camelot-py[cv]>=0.11.0",
        "tabula-py>=2.6.0",
        "numpy>=1.21.0",
        "xlrd>=2.0.0",
        "pdf2image>=1.16.0",
        "pytesseract>=0.3.10",
        "pillow>=9.0.0"
    ]
    
    print("Installing required packages...")
    print("This may take a few minutes.")
    
    import subprocess
    import sys
    
    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package.split('[')[0]])
    
    print("\n✅ All dependencies installed successfully!")
    print("\nNote: For OCR functionality, you also need to install Tesseract:")
    print("  • Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    print("  • macOS: brew install tesseract")
    print("  • Linux: sudo apt-get install tesseract-ocr")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("HIGH-PERFORMANCE PDF TO EXCEL CONVERTER")
    print("Optimized for large files (1000+ rows)")
    print("=" * 70)
    print()
    
    print("Options:")
    print("1. Install dependencies")
    print("2. Convert single PDF file")
    print("3. Convert all PDFs in a folder")
    print("4. Quick convert (command line arguments)")
    print()
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == '1':
        install_dependencies()
    elif choice in ['2', '3']:
        run_batch_conversion()
    elif choice == '4':
        import sys
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            output_path = sys.argv[2] if len(sys.argv) > 2 else None
            max_rows = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else None
            max_cols = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
            
            print(f"Quick converting: {pdf_path}")
            result = quick_convert(pdf_path, output_path, max_rows, max_cols)
            print(f"Output: {result}")
        else:
            print("Usage: python script.py <pdf_path> [output_path] [max_rows] [max_columns]")
    else:
        print("Starting interactive mode...")
        run_batch_conversion()
