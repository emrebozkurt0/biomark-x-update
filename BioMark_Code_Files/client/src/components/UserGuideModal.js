import React from 'react';
import '../css/userGuideModal.css';
// Dynamically build backend URL to avoid hard-coded localhost/port
import { buildUrl } from '../api';
import { helpTexts } from '../content/helpTexts';

const UserGuideModal = ({ onClose }) => {
  return (
    <div className="user-guide-overlay">
      <div className="user-guide-modal">
        <div className="popup-header">
          <h2>Biomarker Analysis Tool - User Guide</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="popup-content">
          <p className="guide-description">
            This tool enables researchers to explore expression datasets to discover potential biomarkers. Upload your data, configure the analysis pipeline, and generate comprehensive visual and statistical reports in just a few clicks.
          </p>
          <div className="video-container">
            {/* Embedded BioMark tutorial video */}
            <iframe
              src="https://www.youtube.com/embed/CDm9amayNTM?rel=0"
              title="BioMark Tutorial"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
          </div>

          {/* Additional tutorial text requested by the user */}
          <div className="guide-steps">
            <p>
              ➡️ Access the source code on GitHub:
              {' '}
              <a
                href="https://github.com/itu-bioinformatics-database-lab/biomark"
                target="_blank"
                rel="noopener noreferrer"
              >
                GitHub Repository
              </a>
            </p>

            <p>
              ➡️ Access the analysis report:
              {' '}
              <a
                href={buildUrl('/analysis-report')}
                target="_blank"
                rel="noopener noreferrer"
              >
                Sample Analysis Report
              </a>
            </p>

            <ol className="guide-step-list">
              <li>
                <strong>Step 1: Loading the Demo Dataset</strong>
                <br />
                Navigate to the BioMark website.
                <br />
                On the homepage, you have two options: upload your own data with the "Browse" button or use the built-in demo data.
                <br />
                To follow along with this tutorial, select the "Use a Demo Dataset for Alzheimer's Disease" option.
              </li>

              <li>
                <strong>Step 2: Configuring the Analysis Groups</strong>
                <br />
                In Step 3 of the tool, you need to select two key columns from your data.
                <br />
                First, select the column that specifies the status of your samples (e.g., patient or healthy). For our demo, this is the "Diagnosis" column.
                <br />
                Next, select the column that contains the unique ID for each sample.
                <br />
                In Step 4, you will see the distribution of patient groups. Choose the classes you want to compare. For this example, we select "AD" (Alzheimer's Disease) and "Control".
                <br />
                Click "Analyze" to proceed.
              </li>

              <li>
                <strong>Step 3: Running Your First Analysis (SHAP)</strong>
                <br />
                In Step 5, choose your desired analysis. BioMark offers a wide array of methods, from differential analysis to clustering and classification. We will start with SHAP, a powerful machine-learning-based method.
                <br />
                In Step 6, exclude any non-numeric or irrelevant columns from the analysis (e.g., "Age", "Gender").
                <br />
                Click "Run Analysis" to start the process.
              </li>

              <li>
                <strong>Step 4: Interpreting Results & Running a Second Analysis (ANOVA)</strong>
                <br />
                Once the analysis is complete, you can explore the interactive SHAP plots to understand the results. The Summary Plot gives a global overview of the most impactful biomarkers, while the Force Plot explains the model's reasoning for a single, specific sample.
                <br />
                To run a comparative analysis, click the "Perform another analysis" button.
                <br />
                This time, select a different method, such as ANOVA, and run the analysis again to get results from a traditional statistical perspective.
              </li>

              <li>
                <strong>Step 5: Creating a Consolidated Biomarker List</strong>
                <br />
                Now that you have results from two different methods (SHAP and ANOVA), it's time to find the most reliable candidates.
                <br />
                Click the "Combine Biomarker List" button.
                <br />
                Select the classes you compared ("AD" and "Control").
                <br />
                BioMark will generate a consensus-based ranking, showing the most robust biomarkers that were identified as important across both methods, giving you higher confidence in your findings.
              </li>

              <li>
                <strong>Step 6: Generating Your Final Report</strong>
                <br />
                Finally, click the "Generate Analysis Report" button to compile all your results into a single, professional document.
                <br />
                The downloadable PDF report is structured to be publication-ready. It strategically begins with your most critical finding—the consolidated biomarker list—and is followed by a detailed breakdown of all the plots from your individual analyses (Waterfall, Force, Summary, Heatmap, ANOVA, etc.).
              </li>
            </ol>
          </div>
          {/* Glossary and Interpreting Results */}
          <div className="guide-steps">
            <h3>Glossary</h3>
            <ul>
              {helpTexts.glossary.items.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
            <h3 style={{ marginTop: '12px' }}>Interpreting Results</h3>
            <p>{helpTexts.glossary.interpreting}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserGuideModal; 