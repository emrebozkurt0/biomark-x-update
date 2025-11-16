const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const router = express.Router();

const getPythonCommand = () => (process.platform === 'win32' ? 'python' : 'python3');

const toRelativeResultPath = (absolutePath) => {
  if (!absolutePath) {
    return absolutePath;
  }

  if (!path.isAbsolute(absolutePath)) {
    return absolutePath.replace(/\\/g, '/');
  }

  const serverRoot = path.join(__dirname, '..');
  return path.relative(serverRoot, absolutePath).replace(/\\/g, '/');
};

const ENRICHMENT_CONFIG = {
  KEGG: {
    geneSet: 'KEGG_2021_Human',
    analysisLabel: 'kegg_pathway_analysis',
    analysisDisplayName: 'KEGG Pathway Analysis',
  },
  GO_BP: {
    geneSet: 'GO_Biological_Process_2021',
    analysisLabel: 'go_biological_process',
    analysisDisplayName: 'GO Biological Process Enrichment',
  },
  GO_CC: {
    geneSet: 'GO_Cellular_Component_2021',
    analysisLabel: 'go_cellular_component',
    analysisDisplayName: 'GO Cellular Component Enrichment',
  },
  GO_MF: {
    geneSet: 'GO_Molecular_Function_2021',
    analysisLabel: 'go_molecular_function',
    analysisDisplayName: 'GO Molecular Function Enrichment',
  },
};

router.post('/pathway-analysis', async (req, res) => {
  const {
    analysisResults,
    selectedClasses = [],
    resultsDir = null,
    analysisType = 'KEGG',
    geneSet = null,
    analysisLabel = null,
    analysisDisplayName = null,
  } = req.body ?? {};

  const sanitizedGenes = Array.isArray(analysisResults)
    ? analysisResults
        .map((gene) => (typeof gene === 'string' ? gene.trim() : ''))
        .filter((gene) => gene.length > 0)
    : [];

  if (sanitizedGenes.length === 0) {
    return res.status(400).json({
      success: false,
      message: 'No significant genes provided for pathway analysis.',
    });
  }

  const pythonCommand = getPythonCommand();
  const scriptPath = path.join(__dirname, '..', 'services', 'pathway_analysis.py');

  let tempDir;
  let geneListFile;

  try {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'biomark-pathway-'));
    geneListFile = path.join(tempDir, 'significant_genes.json');
    fs.writeFileSync(geneListFile, JSON.stringify(sanitizedGenes), 'utf8');
  } catch (err) {
    console.error('Failed to prepare gene list for pathway analysis:', err);
    return res.status(500).json({
      success: false,
      message: 'Failed to prepare input for pathway analysis.',
    });
  }

  const sanitizedClasses = Array.isArray(selectedClasses)
    ? selectedClasses.map((cls) => String(cls).trim()).filter(Boolean)
    : [];
  const classPair = sanitizedClasses.length >= 2 ? `${sanitizedClasses[0]}_${sanitizedClasses[1]}` : '';

  let resolvedResultsDir = path.join(__dirname, '..', 'results');
  if (resultsDir) {
    resolvedResultsDir = path.isAbsolute(resultsDir)
      ? resultsDir
      : path.join(__dirname, '..', resultsDir);
  }

  const normalizedType = typeof analysisType === 'string' && analysisType.trim().length > 0
    ? analysisType.trim().toUpperCase()
    : 'KEGG';
  const defaultConfig = ENRICHMENT_CONFIG[normalizedType] || ENRICHMENT_CONFIG.KEGG;

  const resolvedGeneSet = geneSet || defaultConfig.geneSet;
  const resolvedAnalysisLabel = analysisLabel || defaultConfig.analysisLabel || normalizedType.toLowerCase();
  const resolvedDisplayName = analysisDisplayName || defaultConfig.analysisDisplayName || `${normalizedType} Enrichment`;

  const pythonArgs = [
    '-Xfrozen_modules=off',
    scriptPath,
    geneListFile,
    resolvedResultsDir,
    classPair,
    resolvedGeneSet,
    resolvedAnalysisLabel,
    resolvedDisplayName,
  ];

  console.log('Starting pathway analysis with command:', pythonCommand, pythonArgs.join(' '));

  const python = spawn(pythonCommand, pythonArgs);
  let stdout = '';
  let stderr = '';

  python.stdout.on('data', (data) => {
    stdout += data.toString();
  });

  python.stderr.on('data', (data) => {
    stderr += data.toString();
  });

  python.on('close', (code) => {
    try {
      if (tempDir) {
        fs.rmSync(tempDir, { recursive: true, force: true });
      }
    } catch (cleanupErr) {
      console.warn('Failed to clean up temporary pathway analysis files:', cleanupErr);
    }

    if (code !== 0) {
      console.error('Pathway analysis Python script failed:', stderr || `exit code ${code}`);
      return res.status(500).json({
        success: false,
        message: 'Pathway analysis failed.',
        error: stderr || `Process exited with code ${code}`,
      });
    }

    try {
      const parsed = JSON.parse(stdout.trim());
      console.log('Pathway analysis output:', parsed);

      if (parsed?.data) {
        if (parsed.data.pathwayResults) {
          parsed.data.pathwayResults = toRelativeResultPath(parsed.data.pathwayResults);
        }
        parsed.data.analysisType = normalizedType;
      }

      if (parsed.success) {
        return res.json(parsed);
      }

      return res.status(500).json({
        success: false,
        message: parsed.message || 'Pathway analysis failed.',
        error: parsed.error || null,
        data: parsed.data ?? null,
      });
    } catch (parseErr) {
      console.error('Failed to parse pathway analysis output:', parseErr, stdout);
      return res.status(500).json({
        success: false,
        message: 'Failed to parse pathway analysis output.',
        error: parseErr.toString(),
      });
    }
  });
});

module.exports = router;