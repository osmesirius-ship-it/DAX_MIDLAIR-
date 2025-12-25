/**
 * EDI Integration for DAX MCP Server
 * Provides TypeScript interface to EDI backend for real-time anomaly detection
 */

import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';

export interface EDISensorData {
  sensors: number[][];
  residuals: number[][];
  timestamp: number;
}

export interface EDIOutput {
  salience: number[];
  coherence: number;
  phase_signature: {
    entropy_mean: number;
    residual_mean: number;
    phase_drift_mean: number;
    xcorr_peak_mean: number;
    phase_drift_pairs: number[];
    xcorr_pairs: number[];
    channel_entropies: number[];
    channel_residuals: number[];
    timestamp: number;
  };
  knobs: {
    focus: number;
    entanglement: number;
    interference: number;
    exploration: number;
  };
  risk_assessment: {
    level: 'low' | 'moderate' | 'high' | 'critical';
    score: number;
    actions: string[];
  };
  system_health: {
    health: number;
    trend: number;
    status: 'healthy' | 'degraded' | 'critical' | 'emergency';
    coherence_history_len: number;
  };
  channel_names: string[];
}

export interface GovernanceBias {
  risk_multiplier: number;
  attention_focus: number;
  decision_coupling: number;
  noise_tolerance: number;
  exploration_factor: number;
  coherence_weight: number;
  salience_weights: number[];
}

export class EDIIntegration extends EventEmitter {
  private pythonProcess: ChildProcess | null = null;
  private isConnected = false;
  private responseQueue: Map<string, any> = new Map();
  private messageId = 0;

  constructor(private pythonScriptPath: string = '../backend/edi.py') {
    super();
  }

  /**
   * Start EDI backend process
   */
  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.pythonProcess = spawn('python3', [this.pythonScriptPath], {
          stdio: ['pipe', 'pipe', 'pipe'],
          cwd: process.cwd()
        });

        if (!this.pythonProcess.stdin || !this.pythonProcess.stdout) {
          throw new Error('Failed to create stdin/stdout pipes');
        }

        this.pythonProcess.stdout.on('data', (data) => {
          this.handleResponse(data.toString());
        });

        this.pythonProcess.stderr.on('data', (data) => {
          console.error('EDI Error:', data.toString());
          this.emit('error', data.toString());
        });

        this.pythonProcess.on('close', (code) => {
          this.isConnected = false;
          console.log(`EDI process exited with code ${code}`);
          this.emit('disconnected');
        });

        this.pythonProcess.on('error', (error) => {
          console.error('EDI Process Error:', error);
          this.emit('error', error);
          reject(error);
        });

        // Wait for process to be ready
        setTimeout(() => {
          this.isConnected = true;
          this.emit('connected');
          resolve();
        }, 1000);

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Stop EDI backend process
   */
  async stop(): Promise<void> {
    if (this.pythonProcess) {
      this.pythonProcess.kill();
      this.pythonProcess = null;
    }
    this.isConnected = false;
  }

  /**
   * Process sensor data through EDI
   */
  async processSensorData(sensors: number[][], residuals: number[][]): Promise<EDIOutput> {
    if (!this.isConnected || !this.pythonProcess) {
      throw new Error('EDI not connected');
    }

    const message = {
      id: ++this.messageId,
      type: 'process_sensor_data',
      data: { sensors, residuals }
    };

    return this.sendMessage(message);
  }

  /**
   * Get current governance bias parameters
   */
  async getGovernanceBias(): Promise<GovernanceBias> {
    if (!this.isConnected || !this.pythonProcess) {
      throw new Error('EDI not connected');
    }

    const message = {
      id: ++this.messageId,
      type: 'get_governance_bias',
      data: {}
    };

    return this.sendMessage(message);
  }

  /**
   * Get system health status
   */
  async getSystemHealth(): Promise<any> {
    if (!this.isConnected || !this.pythonProcess) {
      throw new Error('EDI not connected');
    }

    const message = {
      id: ++this.messageId,
      type: 'get_system_health',
      data: {}
    };

    return this.sendMessage(message);
  }

  /**
   * Send message to EDI process and wait for response
   */
  private async sendMessage(message: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const id = message.id;
      
      // Store response handler
      this.responseQueue.set(id, { resolve, reject });
      
      // Set timeout
      setTimeout(() => {
        if (this.responseQueue.has(id)) {
          this.responseQueue.delete(id);
          reject(new Error('EDI request timeout'));
        }
      }, 10000);

      // Send message
      const messageStr = JSON.stringify(message) + '\n';
      this.pythonProcess?.stdin?.write(messageStr);
    });
  }

  /**
   * Handle response from EDI process
   */
  private handleResponse(data: string) {
    try {
      const lines = data.trim().split('\n');
      for (const line of lines) {
        if (line.trim()) {
          const response = JSON.parse(line);
          const { id, type, result, error } = response;

          if (this.responseQueue.has(id)) {
            const { resolve, reject } = this.responseQueue.get(id)!;
            this.responseQueue.delete(id);

            if (error) {
              reject(new Error(error));
            } else {
              resolve(result);
            }
          }

          // Emit events for real-time updates
          this.emit(type, result);
        }
      }
    } catch (error) {
      console.error('Failed to parse EDI response:', error);
    }
  }

  /**
   * Check if EDI is connected
   */
  isReady(): boolean {
    return this.isConnected;
  }
}

/**
 * EDI-enabled DAX Governance Core
 */
export class EDIEnabledDAXCore {
  private edi: EDIIntegration;
  private governanceBias: GovernanceBias = {
    risk_multiplier: 1.0,
    attention_focus: 0.8,
    decision_coupling: 0.5,
    noise_tolerance: 0.3,
    exploration_factor: 0.4,
    coherence_weight: 1.0,
    salience_weights: [0.25, 0.25, 0.25, 0.25]
  };

  constructor(ediScriptPath?: string) {
    this.edi = new EDIIntegration(ediScriptPath);
  }

  /**
   * Initialize EDI and DAX integration
   */
  async initialize(): Promise<void> {
    await this.edi.start();
    console.log('EDI-DAX integration initialized');
  }

  /**
   * Process request through DAX governance with EDI bias
   */
  async runGovernance(input: string, sensorData?: EDISensorData): Promise<any> {
    let ediOutput: EDIOutput | null = null;

    // Process sensor data through EDI if available
    if (sensorData) {
      try {
        ediOutput = await this.edi.processSensorData(
          sensorData.sensors,
          sensorData.residuals
        );
        
        // Update governance bias based on EDI output
        this.governanceBias = await this.edi.getGovernanceBias();
        
      } catch (error) {
        console.error('EDI processing failed:', error);
        // Continue with default bias
      }
    }

    // Apply EDI bias to governance processing
    const governanceResult = await this.processWithBias(input, ediOutput);
    
    return governanceResult;
  }

  /**
   * Process input with EDI bias applied
   */
  private async processWithBias(input: string, ediOutput: EDIOutput | null): Promise<any> {
    // Simulate DAX governance processing with bias
    const baseResult: any = {
      output: `Governed response to: ${input}`,
      trace: [],
      beliefs: {
        coherence: 0.8,
        reliability: 0.9,
        hallucination_risk: 0.1
      }
    };

    if (ediOutput) {
      // Apply EDI bias to results
      baseResult.beliefs.coherence *= ediOutput.coherence;
      baseResult.beliefs.reliability *= (1 - ediOutput.risk_assessment.score);
      baseResult.beliefs.hallucination_risk += ediOutput.risk_assessment.score * 0.2;
      
      // Add EDI metadata
      baseResult.edi_metadata = {
        coherence: ediOutput.coherence,
        risk_level: ediOutput.risk_assessment.level,
        system_health: ediOutput.system_health.status,
        governance_bias: this.governanceBias
      };
    }

    return baseResult;
  }

  /**
   * Generate chat response with EDI integration
   */
  async generateChat(params: {
    message: string;
    sessionId?: string;
    includeGovernance?: boolean;
    context?: string[];
    sensorData?: EDISensorData;
  }): Promise<any> {
    const governanceResult = await this.runGovernance(
      params.message,
      params.sensorData
    );

    return {
      response: governanceResult.output,
      sessionId: params.sessionId || `session_${Date.now()}`,
      timestamp: new Date().toISOString(),
      beliefs: governanceResult.beliefs,
      governanceTrace: governanceResult.trace,
      ediMetadata: governanceResult.edi_metadata
    };
  }

  /**
   * Get current system status
   */
  async getSystemStatus(): Promise<any> {
    const ediHealth = await this.edi.getSystemHealth();
    
    return {
      dax_status: 'operational',
      edi_status: ediHealth,
      governance_bias: this.governanceBias,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Shutdown integration
   */
  async shutdown(): Promise<void> {
    await this.edi.stop();
  }
}

/**
 * MCP Tool Integration for EDI
 */
export class EDITools {
  constructor(private ediCore: EDIEnabledDAXCore) {}

  /**
   * Process sensor data through EDI
   */
  async processSensorDataTool(args: {
    sensors: number[][];
    residuals: number[][];
  }): Promise<EDIOutput> {
    return await this.ediCore['edi'].processSensorData(args.sensors, args.residuals);
  }

  /**
   * Get EDI system health
   */
  async getEDIHealthTool(): Promise<any> {
    return await this.ediCore.getSystemStatus();
  }

  /**
   * Run governance with EDI bias
   */
  async runGovernanceWithEDITool(args: {
    input: string;
    sensorData?: EDISensorData;
  }): Promise<any> {
    return await this.ediCore.runGovernance(args.input, args.sensorData);
  }
}

export default EDIEnabledDAXCore;
