#!/usr/bin/env python3
"""
Advanced ML Engine for Testing
Módulo central de ML com algoritmos avançados para testing automation
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import pickle
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MLPrediction:
    prediction: float
    confidence: float
    reasoning: List[str]
    model_used: str

@dataclass
class TestMetrics:
    test_name: str
    execution_time: float
    failure_rate: float
    code_coverage: float
    business_impact: str
    last_execution: datetime
    flakiness_score: float

class AdvancedMLEngine:
    
    def __init__(self):
        self.models = {
            'failure_predictor': None,
            'priority_optimizer': None,
            'flakiness_detector': None,
            'performance_predictor': None
        }
        self.scalers = {}
        self.encoders = {}
        self.model_metrics = {}
        self.training_history = []
        
    def train_failure_prediction_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Treina modelo para predizer falhas de testes"""
        try:
            if len(training_data) < 50:
                return {'error': 'Insufficient data for failure prediction (minimum 50 samples)'}
            
            # Preparar dados
            df = pd.DataFrame(training_data)
            
            # Features engineering
            features = self._extract_failure_features(df)
            target = df['failed'].astype(int)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=0.2, random_state=42, stratify=target
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train ensemble model
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            mlp_model = MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
            
            rf_model.fit(X_train_scaled, y_train)
            mlp_model.fit(X_train_scaled, y_train)
            
            # Evaluate models
            rf_score = rf_model.score(X_test_scaled, y_test)
            mlp_score = mlp_model.score(X_test_scaled, y_test)
            
            # Choose best model
            if rf_score > mlp_score:
                self.models['failure_predictor'] = rf_model
                best_score = rf_score
                model_type = 'RandomForest'
            else:
                self.models['failure_predictor'] = mlp_model
                best_score = mlp_score
                model_type = 'NeuralNetwork'
            
            self.scalers['failure_predictor'] = scaler
            self.model_metrics['failure_predictor'] = {
                'accuracy': best_score,
                'model_type': model_type,
                'training_samples': len(training_data),
                'features': list(features.columns)
            }
            
            # Save model
            self._save_model('failure_predictor')
            
            return {
                'success': True,
                'accuracy': best_score,
                'model_type': model_type,
                'feature_importance': self._get_feature_importance('failure_predictor', features.columns)
            }
            
        except Exception as e:
            return {'error': f'Training failed: {str(e)}'}
    
    def predict_test_failure(self, test_metrics: TestMetrics) -> MLPrediction:
        """Prediz probabilidade de falha de um teste"""
        if not self.models['failure_predictor']:
            return MLPrediction(0.5, 0.0, ['No model trained'], 'None')
        
        try:
            # Preparar features
            features = self._prepare_test_features(test_metrics)
            features_scaled = self.scalers['failure_predictor'].transform([features])
            
            # Predição
            if hasattr(self.models['failure_predictor'], 'predict_proba'):
                proba = self.models['failure_predictor'].predict_proba(features_scaled)[0]
                failure_prob = proba[1] if len(proba) > 1 else proba[0]
                confidence = max(proba) - min(proba)  # Diferença entre classes
            else:
                failure_prob = self.models['failure_predictor'].predict(features_scaled)[0]
                confidence = 0.7  # Default confidence
            
            # Gerar reasoning
            reasoning = self._generate_failure_reasoning(test_metrics, failure_prob)
            
            return MLPrediction(
                prediction=float(failure_prob),
                confidence=float(confidence),
                reasoning=reasoning,
                model_used=self.model_metrics['failure_predictor']['model_type']
            )
            
        except Exception as e:
            return MLPrediction(0.5, 0.0, [f'Prediction error: {str(e)}'], 'Error')
    
    def train_flakiness_detector(self, execution_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Treina detector de testes flaky usando clustering"""
        try:
            if len(execution_history) < 30:
                return {'error': 'Insufficient execution history (minimum 30 executions)'}
            
            # Preparar dados para clustering
            df = pd.DataFrame(execution_history)
            
            # Features para flakiness
            flaky_features = self._extract_flakiness_features(df)
            
            # DBSCAN para detectar outliers (testes flaky)
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(flaky_features)
            
            dbscan = DBSCAN(eps=0.5, min_samples=3)
            clusters = dbscan.fit_predict(features_scaled)
            
            # Identificar cluster de testes flaky (outliers = -1)
            flaky_indices = np.where(clusters == -1)[0]
            
            self.models['flakiness_detector'] = dbscan
            self.scalers['flakiness_detector'] = scaler
            
            flakiness_rate = len(flaky_indices) / len(execution_history)
            
            return {
                'success': True,
                'flaky_tests_detected': len(flaky_indices),
                'flakiness_rate': flakiness_rate,
                'clusters_found': len(set(clusters)) - (1 if -1 in clusters else 0)
            }
            
        except Exception as e:
            return {'error': f'Flakiness detection training failed: {str(e)}'}
    
    def detect_flaky_test(self, test_executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detecta se um teste é flaky baseado no histórico"""
        if not self.models['flakiness_detector'] or len(test_executions) < 5:
            return {'is_flaky': False, 'confidence': 0.0, 'reasoning': ['Insufficient data']}
        
        try:
            # Calcular métricas de flakiness
            success_rate = sum(1 for exec in test_executions if exec.get('passed', False)) / len(test_executions)
            
            # Variabilidade no tempo de execução
            exec_times = [exec.get('execution_time', 0) for exec in test_executions]
            time_variance = np.var(exec_times) if exec_times else 0
            
            # Padrão de falhas
            failures = [not exec.get('passed', True) for exec in test_executions]
            failure_pattern_score = self._calculate_failure_pattern_score(failures)
            
            # Features para clustering
            features = [success_rate, time_variance, failure_pattern_score, len(test_executions)]
            features_scaled = self.scalers['flakiness_detector'].transform([features])
            
            # Predição
            cluster = self.models['flakiness_detector'].fit_predict(features_scaled)[0]
            is_flaky = cluster == -1  # Outlier = flaky
            
            # Calcular confiança
            confidence = 1.0 - success_rate if is_flaky else success_rate
            
            reasoning = []
            if success_rate < 0.8:
                reasoning.append(f'Low success rate: {success_rate:.1%}')
            if time_variance > 100:
                reasoning.append('High execution time variance')
            if failure_pattern_score > 0.5:
                reasoning.append('Irregular failure pattern detected')
            
            return {
                'is_flaky': is_flaky,
                'confidence': confidence,
                'success_rate': success_rate,
                'flakiness_score': 1.0 - success_rate,
                'reasoning': reasoning
            }
            
        except Exception as e:
            return {'is_flaky': False, 'confidence': 0.0, 'reasoning': [f'Detection error: {str(e)}']}
    
    def train_performance_predictor(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Treina modelo para predizer tempo de execução"""
        try:
            if len(performance_data) < 40:
                return {'error': 'Insufficient performance data (minimum 40 samples)'}
            
            df = pd.DataFrame(performance_data)
            
            # Features para predição de performance
            features = self._extract_performance_features(df)
            target = df['execution_time']
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=0.2, random_state=42
            )
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Gradient Boosting for regression
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            predictions = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, predictions)
            r2_score = model.score(X_test_scaled, y_test)
            
            self.models['performance_predictor'] = model
            self.scalers['performance_predictor'] = scaler
            self.model_metrics['performance_predictor'] = {
                'mse': mse,
                'r2_score': r2_score,
                'training_samples': len(performance_data)
            }
            
            return {
                'success': True,
                'r2_score': r2_score,
                'mse': mse,
                'feature_importance': self._get_feature_importance('performance_predictor', features.columns)
            }
            
        except Exception as e:
            return {'error': f'Performance prediction training failed: {str(e)}'}
    
    def predict_execution_time(self, test_characteristics: Dict[str, Any]) -> MLPrediction:
        """Prediz tempo de execução de um teste"""
        if not self.models['performance_predictor']:
            return MLPrediction(60.0, 0.0, ['No model trained'], 'None')
        
        try:
            # Preparar features
            features = self._prepare_performance_features(test_characteristics)
            features_scaled = self.scalers['performance_predictor'].transform([features])
            
            # Predição
            predicted_time = self.models['performance_predictor'].predict(features_scaled)[0]
            
            # Calcular confiança baseada no R² do modelo
            confidence = self.model_metrics['performance_predictor']['r2_score']
            
            reasoning = self._generate_performance_reasoning(test_characteristics, predicted_time)
            
            return MLPrediction(
                prediction=float(predicted_time),
                confidence=float(confidence),
                reasoning=reasoning,
                model_used='GradientBoosting'
            )
            
        except Exception as e:
            return MLPrediction(60.0, 0.0, [f'Prediction error: {str(e)}'], 'Error')
    
    def _extract_failure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrai features para predição de falhas"""
        features = pd.DataFrame()
        
        features['execution_time'] = df['execution_time']
        features['code_coverage'] = df.get('code_coverage', 50)
        features['complexity_score'] = df.get('complexity_score', 1)
        features['recent_changes'] = df.get('recent_changes', 0).astype(int)
        features['failure_history'] = df.get('failure_count', 0)
        
        # Features categóricas
        if 'test_type' in df.columns:
            le = LabelEncoder()
            features['test_type_encoded'] = le.fit_transform(df['test_type'])
            self.encoders['test_type'] = le
        
        return features
    
    def _extract_flakiness_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrai features para detecção de flakiness"""
        features = pd.DataFrame()
        
        # Agrupar por teste
        test_groups = df.groupby('test_name')
        
        for test_name, group in test_groups:
            success_rate = group['passed'].mean()
            exec_time_var = group['execution_time'].var()
            failure_streak = self._calculate_failure_streaks(group['passed'].tolist())
            
            features = pd.concat([features, pd.DataFrame({
                'success_rate': [success_rate],
                'time_variance': [exec_time_var],
                'failure_streaks': [failure_streak],
                'total_executions': [len(group)]
            })], ignore_index=True)
        
        return features.fillna(0)
    
    def _extract_performance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrai features para predição de performance"""
        features = pd.DataFrame()
        
        features['code_lines'] = df.get('code_lines', 100)
        features['complexity'] = df.get('complexity_score', 1)
        features['dependencies'] = df.get('dependency_count', 0)
        features['io_operations'] = df.get('io_operations', 0)
        features['network_calls'] = df.get('network_calls', 0)
        
        return features
    
    def _prepare_test_features(self, test_metrics: TestMetrics) -> List[float]:
        """Prepara features de um teste para predição"""
        return [
            test_metrics.execution_time,
            test_metrics.code_coverage,
            test_metrics.failure_rate,
            test_metrics.flakiness_score,
            1 if test_metrics.business_impact == 'CRITICAL' else 0
        ]
    
    def _prepare_performance_features(self, characteristics: Dict[str, Any]) -> List[float]:
        """Prepara features para predição de performance"""
        return [
            characteristics.get('code_lines', 100),
            characteristics.get('complexity_score', 1),
            characteristics.get('dependency_count', 0),
            characteristics.get('io_operations', 0),
            characteristics.get('network_calls', 0)
        ]
    
    def _calculate_failure_pattern_score(self, failures: List[bool]) -> float:
        """Calcula score do padrão de falhas"""
        if not failures:
            return 0.0
        
        # Detectar alternância entre sucesso/falha (indicativo de flakiness)
        alternations = sum(1 for i in range(1, len(failures)) if failures[i] != failures[i-1])
        max_alternations = len(failures) - 1
        
        return alternations / max_alternations if max_alternations > 0 else 0.0
    
    def _calculate_failure_streaks(self, results: List[bool]) -> float:
        """Calcula streaks de falhas"""
        if not results:
            return 0.0
        
        streaks = []
        current_streak = 0
        
        for result in results:
            if not result:  # Falha
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(current_streak)
                current_streak = 0
        
        if current_streak > 0:
            streaks.append(current_streak)
        
        return max(streaks) if streaks else 0.0
    
    def _generate_failure_reasoning(self, test_metrics: TestMetrics, failure_prob: float) -> List[str]:
        """Gera reasoning para predição de falha"""
        reasoning = []
        
        if failure_prob > 0.7:
            reasoning.append('HIGH RISK: Strong failure indicators detected')
        
        if test_metrics.failure_rate > 0.3:
            reasoning.append(f'High historical failure rate: {test_metrics.failure_rate:.1%}')
        
        if test_metrics.flakiness_score > 0.5:
            reasoning.append('Test shows flaky behavior patterns')
        
        if test_metrics.execution_time > 300:
            reasoning.append('Long execution time increases failure risk')
        
        return reasoning or ['Standard risk assessment']
    
    def _generate_performance_reasoning(self, characteristics: Dict[str, Any], predicted_time: float) -> List[str]:
        """Gera reasoning para predição de performance"""
        reasoning = []
        
        if predicted_time > 300:
            reasoning.append('Long execution predicted due to complexity')
        
        if characteristics.get('network_calls', 0) > 5:
            reasoning.append('Multiple network calls increase execution time')
        
        if characteristics.get('io_operations', 0) > 10:
            reasoning.append('High I/O operations detected')
        
        return reasoning or ['Standard performance prediction']
    
    def _get_feature_importance(self, model_name: str, feature_names: List[str]) -> Dict[str, float]:
        """Obtém importância das features"""
        model = self.models.get(model_name)
        if model and hasattr(model, 'feature_importances_'):
            return dict(zip(feature_names, model.feature_importances_))
        return {}
    
    def _save_model(self, model_name: str):
        """Salva modelo treinado"""
        try:
            os.makedirs('models', exist_ok=True)
            
            with open(f'models/{model_name}.pkl', 'wb') as f:
                pickle.dump(self.models[model_name], f)
            
            if model_name in self.scalers:
                with open(f'models/{model_name}_scaler.pkl', 'wb') as f:
                    pickle.dump(self.scalers[model_name], f)
        except Exception:
            pass
    
    def load_models(self) -> Dict[str, bool]:
        """Carrega todos os modelos salvos"""
        results = {}
        
        for model_name in self.models.keys():
            try:
                with open(f'models/{model_name}.pkl', 'rb') as f:
                    self.models[model_name] = pickle.load(f)
                
                try:
                    with open(f'models/{model_name}_scaler.pkl', 'rb') as f:
                        self.scalers[model_name] = pickle.load(f)
                except:
                    pass
                
                results[model_name] = True
            except:
                results[model_name] = False
        
        return results
    
    def get_model_status(self) -> Dict[str, Any]:
        """Retorna status de todos os modelos"""
        status = {}
        
        for model_name, model in self.models.items():
            status[model_name] = {
                'trained': model is not None,
                'metrics': self.model_metrics.get(model_name, {}),
                'last_update': datetime.now().isoformat()
            }
        
        return status

def main():
    """Exemplo de uso do Advanced ML Engine"""
    engine = AdvancedMLEngine()
    
    print("Advanced ML Engine for Testing")
    print("=" * 50)
    
    # Carregar modelos existentes
    load_results = engine.load_models()
    print(f"Models loaded: {sum(load_results.values())}/{len(load_results)}")
    
    # Simular dados de treinamento para failure prediction
    print("\nTraining failure prediction model...")
    failure_training_data = []
    
    for i in range(100):
        failure_training_data.append({
            'execution_time': np.random.uniform(10, 300),
            'code_coverage': np.random.uniform(40, 95),
            'complexity_score': np.random.uniform(1, 10),
            'recent_changes': np.random.randint(0, 2),
            'failure_count': np.random.randint(0, 10),
            'test_type': np.random.choice(['UNIT', 'INTEGRATION', 'API']),
            'failed': np.random.choice([0, 1], p=[0.8, 0.2])  # 20% failure rate
        })
    
    failure_result = engine.train_failure_prediction_model(failure_training_data)
    if failure_result.get('success'):
        print(f"[SUCCESS] Failure prediction model trained! Accuracy: {failure_result['accuracy']:.3f}")
    
    # Testar predição de falha
    test_metrics = TestMetrics(
        test_name="test_critical_function",
        execution_time=120.0,
        failure_rate=0.15,
        code_coverage=85.0,
        business_impact="CRITICAL",
        last_execution=datetime.now(),
        flakiness_score=0.3
    )
    
    prediction = engine.predict_test_failure(test_metrics)
    print(f"\nFailure Prediction:")
    print(f"   Probability: {prediction.prediction:.3f}")
    print(f"   Confidence: {prediction.confidence:.3f}")
    print(f"   Reasoning: {prediction.reasoning}")
    
    # Status dos modelos
    print(f"\nModel Status:")
    status = engine.get_model_status()
    for model_name, info in status.items():
        print(f"   {model_name}: {'[TRAINED]' if info['trained'] else '[NOT TRAINED]'}")

if __name__ == "__main__":
    main()