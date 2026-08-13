# holonic/ubec_holonic_cli.py

import os
import sys
import argparse
import logging
import json
from datetime import datetime

# Ensure the parent directory is in the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the holonic evaluator and visualizer
from holonic.ubec_holonic_evaluator import UBECHolonicEvaluator
from holonic.ubec_holonic_visualizer import UBECHolonicVisualizer

def setup_logging(log_level='INFO', log_file=None):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: File to log to (in addition to console)
    """
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def evaluate_accounts(args):
    """
    Run the holonic evaluation process.
    
    Args:
        args: Command-line arguments
    """
    logging.info("Starting UBEC holonic evaluation")
    
    try:
        # Create evaluator with the specified config
        evaluator = UBECHolonicEvaluator(config_path=args.config)
        
        # Customize thresholds if needed
        if args.thresholds:
            try:
                with open(args.thresholds, 'r') as f:
                    custom_thresholds = json.load(f)
                
                # Update thresholds
                for category, values in custom_thresholds.items():
                    if category in evaluator.thresholds:
                        evaluator.thresholds[category].update(values)
                
                logging.info(f"Loaded custom thresholds from {args.thresholds}")
            except Exception as e:
                logging.error(f"Error loading thresholds file: {e}")
        
        # Run the evaluation
        evaluation_report = evaluator.run_evaluation()
        
        # Save the report
        if args.output:
            output_file = args.output
        else:
            # Generate a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"ubec_holonic_report_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(evaluation_report, f, indent=2)
        
        logging.info(f"Evaluation report saved to {output_file}")
        
        return output_file, evaluator
    
    except Exception as e:
        logging.error(f"Error in evaluation process: {e}")
        raise

def visualize_report(args, report_file=None, evaluator=None):
    """
    Generate visualizations from the evaluation report.
    
    Args:
        args: Command-line arguments
        report_file: Path to report file (if already generated)
        evaluator: UBECHolonicEvaluator instance (if available)
    """
    logging.info("Generating visualizations")
    
    try:
        # Use the provided report file or the one specified in args
        if not report_file:
            report_file = args.report
        
        # Create visualizer
        visualizer = UBECHolonicVisualizer(report_file)
        
        # If we have the evaluator, add the transaction network to the visualizer
        if evaluator and hasattr(evaluator, 'transaction_network'):
            visualizer.transaction_network = evaluator.transaction_network
        
        # Create output directory if it doesn't exist
        output_dir = args.viz_output or "visualizations"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate the requested visualizations
        if args.all_viz or args.score_dist:
            score_dist_file = os.path.join(output_dir, f"score_distribution_{timestamp}.png")
            visualizer.create_score_distribution_chart(score_dist_file)
            logging.info(f"Score distribution chart saved to {score_dist_file}")
        
        if args.all_viz or args.radar:
            radar_file = os.path.join(output_dir, f"radar_chart_{timestamp}.png")
            visualizer.create_radar_chart(output_file=radar_file)
            logging.info(f"Radar chart saved to {radar_file}")
        
        if args.all_viz or args.category_dist:
            category_file = os.path.join(output_dir, f"category_distribution_{timestamp}.png")
            visualizer.create_category_distribution_chart(category_file)
            logging.info(f"Category distribution chart saved to {category_file}")
        
        if (args.all_viz or args.network) and hasattr(visualizer, 'transaction_network'):
            network_file = os.path.join(output_dir, f"network_visualization_{timestamp}.png")
            visualizer.create_network_visualization(network_file)
            logging.info(f"Network visualization saved to {network_file}")
        
        if args.html_report:
            html_report = visualizer.generate_html_report(output_dir=output_dir)
            logging.info(f"HTML report generated: {html_report}")
        
        return True
    
    except Exception as e:
        logging.error(f"Error generating visualizations: {e}")
        return False

def main():
    """
    Main entry point for the UBEC Holonic CLI.
    """
    parser = argparse.ArgumentParser(
        description="UBEC Holonic Evaluation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Run a full evaluation with all visualizations:
    python ubec_holonic_cli.py evaluate --all-viz --html-report
    
  Visualize an existing report:
    python ubec_holonic_cli.py visualize --report report.json --all-viz
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Run holonic evaluation')
    eval_parser.add_argument('--config', default='../config/settings.py',
                           help='Path to config/settings.py file')
    eval_parser.add_argument('--output', help='Output filename for the evaluation report')
    eval_parser.add_argument('--thresholds', help='JSON file with custom metric thresholds')
    eval_parser.add_argument('--log-level', default='INFO',
                          choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                          help='Logging level')
    eval_parser.add_argument('--log-file', help='Log to file (in addition to console)')
    
    # Add visualization options to evaluate command
    eval_parser.add_argument('--all-viz', action='store_true',
                          help='Generate all visualizations')
    eval_parser.add_argument('--score-dist', action='store_true',
                          help='Generate score distribution chart')
    eval_parser.add_argument('--radar', action='store_true',
                          help='Generate radar chart')
    eval_parser.add_argument('--category-dist', action='store_true',
                          help='Generate category distribution chart')
    eval_parser.add_argument('--network', action='store_true',
                          help='Generate network visualization')
    eval_parser.add_argument('--html-report', action='store_true',
                          help='Generate HTML report')
    eval_parser.add_argument('--viz-output', help='Directory for visualization outputs')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualizations from an existing report')
    viz_parser.add_argument('--report', required=True,
                          help='Path to evaluation report JSON file')
    viz_parser.add_argument('--all-viz', action='store_true',
                          help='Generate all visualizations')
    viz_parser.add_argument('--score-dist', action='store_true',
                          help='Generate score distribution chart')
    viz_parser.add_argument('--radar', action='store_true',
                          help='Generate radar chart')
    viz_parser.add_argument('--category-dist', action='store_true',
                          help='Generate category distribution chart')
    viz_parser.add_argument('--network', action='store_true',
                          help='Generate network visualization')
    viz_parser.add_argument('--html-report', action='store_true',
                          help='Generate HTML report')
    viz_parser.add_argument('--viz-output', help='Directory for visualization outputs')
    viz_parser.add_argument('--log-level', default='INFO',
                          choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                          help='Logging level')
    viz_parser.add_argument('--log-file', help='Log to file (in addition to console)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    log_level = getattr(args, 'log_level', 'INFO')
    log_file = getattr(args, 'log_file', None)
    setup_logging(log_level, log_file)
    
    if args.command == 'evaluate':
        # Run evaluation
        try:
            report_file, evaluator = evaluate_accounts(args)
            
            # If visualizations are requested, generate them
            if any([args.all_viz, args.score_dist, args.radar, 
                    args.category_dist, args.network, args.html_report]):
                visualize_report(args, report_file, evaluator)
                
            logging.info("Evaluation completed successfully")
            return 0
        
        except Exception as e:
            logging.error(f"Evaluation failed: {e}")
            return 1
            
    elif args.command == 'visualize':
        # Generate visualizations from an existing report
        if not os.path.exists(args.report):
            logging.error(f"Report file not found: {args.report}")
            return 1
            
        try:
            success = visualize_report(args)
            if success:
                logging.info("Visualization completed successfully")
                return 0
            else:
                logging.error("Visualization failed")
                return 1
        
        except Exception as e:
            logging.error(f"Visualization failed: {e}")
            return 1
    
    else:
        # No command specified
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())