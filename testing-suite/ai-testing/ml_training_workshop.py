#!/usr/bin/env python3
"""
ML Training Workshop - Hands-on para QA Engineers
Aprenda a treinar modelos ML para testing na prática
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import pickle
import os
from typing import List, Dict, Any

class MLTrainingWorkshop:
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.training_results = {}
        
        # Criar diretórios necessários
        os.makedirs('models', exist_ok=True)
        os.makedirs('reports_ml', exist_ok=True)
        
    def generate_synthetic_test_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Gera dados sintéticos realistas para treinamento"""
        print(f"🔄 Gerando {n_samples} amostras de dados sintéticos...")
        
        np.random.seed(42)
        
        # Features básicas
        data = {
            'test_name': [f'test_{i:04d}' for i in range(n_samples)],
            'execution_time': np.random.lognormal(3, 1, n_samples),  # Log-normal para tempos realistas
            'code_coverage': np.random.beta(8, 2, n_samples) * 100,  # Beta para cobertura
            'complexity_score': np.random.gamma(2, 2, n_samples),
            'lines_of_code': np.random.poisson(150, n_samples),
            'failure_count': np.random.poisson(2, n_samples),
            'days_since_last_failure': np.random.exponential(30, n_samples),
            'test_type': np.random.choice(['UNIT', 'INTEGRATION', 'API', 'UI', 'SECURITY'], n_samples, 
                                        p=[0.4, 0.25, 0.15, 0.1, 0.1]),
            'business_impact': np.random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], n_samples,
                                             p=[0.3, 0.4, 0.2, 0.1]),
            'recent_changes': np.random.binomial(1, 0.3, n_samples),  # 30% chance de mudanças recentes
            'dependency_count': np.random.poisson(5, n_samples),
            'io_operations': np.random.poisson(3, n_samples),
            'network_calls': np.random.poisson(2, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Criar target variables baseadas em lógica realista
        
        # 1. Probabilidade de falha (failure_probability)
        failure_prob = (
            (df['failure_count'] / 10) * 0.3 +
            (df['complexity_score'] / 10) * 0.2 +
            (df['recent_changes']) * 0.2 +
            (df['execution_time'] / 300) * 0.1 +
            ((df['business_impact'] == 'CRITICAL').astype(int)) * 0.2
        )
        df['failure_probability'] = np.clip(failure_prob, 0, 1)
        df['will_fail'] = (df['failure_probability'] > 0.6).astype(int)
        
        # 2. Prioridade de teste (test_priority)
        priority_score = (
            (df['business_impact'].map({'LOW': 0.2, 'MEDIUM': 0.4, 'HIGH': 0.7, 'CRITICAL': 1.0})) * 0.3 +
            (df['failure_count'] / 10) * 0.25 +
            (df['code_coverage'] / 100) * 0.2 +
            (df['recent_changes']) * 0.15 +
            (1 / (1 + df['execution_time'] / 60)) * 0.1  # Testes rápidos têm prioridade
        )
        df['test_priority'] = np.clip(priority_score, 0, 1)
        
        # 3. Flakiness score
        flakiness = (
            (df['failure_count'] > 3).astype(int) * 0.4 +
            (df['complexity_score'] > 5).astype(int) * 0.3 +
            (df['network_calls'] > 2).astype(int) * 0.3
        )
        df['is_flaky'] = (flakiness > 0.5).astype(int)
        
        print(f"✅ Dados gerados com sucesso!")
        print(f"   • Testes que falharão: {df['will_fail'].sum()} ({df['will_fail'].mean():.1%})")
        print(f"   • Testes flaky: {df['is_flaky'].sum()} ({df['is_flaky'].mean():.1%})")
        print(f"   • Prioridade média: {df['test_priority'].mean():.3f}")
        
        return df
    
    def workshop_1_failure_prediction(self, df: pd.DataFrame):
        """Workshop 1: Treinar modelo para predizer falhas de testes"""
        print("\n" + "="*60)
        print("🎯 WORKSHOP 1: PREDIÇÃO DE FALHAS DE TESTES")
        print("="*60)
        
        # Preparar features
        feature_columns = [
            'execution_time', 'code_coverage', 'complexity_score', 
            'failure_count', 'days_since_last_failure', 'recent_changes',
            'dependency_count', 'io_operations', 'network_calls'
        ]
        
        # Encoding categórico
        le_test_type = LabelEncoder()
        le_business = LabelEncoder()
        
        df_encoded = df.copy()
        df_encoded['test_type_encoded'] = le_test_type.fit_transform(df['test_type'])
        df_encoded['business_impact_encoded'] = le_business.fit_transform(df['business_impact'])
        
        feature_columns.extend(['test_type_encoded', 'business_impact_encoded'])
        
        X = df_encoded[feature_columns]
        y = df_encoded['will_fail']
        
        print(f"📊 Dataset: {len(X)} amostras, {len(feature_columns)} features")
        print(f"   • Classe positiva (falhas): {y.sum()} ({y.mean():.1%})")
        
        # Split dos dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normalização
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        print(f"\n🔧 Treinando modelo Random Forest...")
        
        # Hyperparameter tuning
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, None],
            'min_samples_split': [2, 5, 10]
        }
        
        rf = RandomForestClassifier(random_state=42)
        grid_search = GridSearchCV(
            rf, param_grid, cv=5, scoring='f1', n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X_train_scaled, y_train)
        best_model = grid_search.best_estimator_
        
        # Avaliação
        y_pred = best_model.predict(X_test_scaled)
        y_proba = best_model.predict_proba(X_test_scaled)[:, 1]
        
        # Métricas
        accuracy = best_model.score(X_test_scaled, y_test)
        auc_roc = roc_auc_score(y_test, y_proba)
        
        print(f"\n📈 RESULTADOS DO MODELO:")
        print(f"   • Melhores parâmetros: {grid_search.best_params_}")
        print(f"   • Acurácia: {accuracy:.3f}")
        print(f"   • AUC-ROC: {auc_roc:.3f}")
        print(f"   • F1-Score (CV): {grid_search.best_score_:.3f}")
        
        # Classification report
        print(f"\n📋 Relatório de Classificação:")
        print(classification_report(y_test, y_pred))
        
        # Feature importance
        feature_importance = dict(zip(feature_columns, best_model.feature_importances_))
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n🔍 Top 5 Features Mais Importantes:")
        for feature, importance in sorted_features[:5]:
            print(f"   • {feature}: {importance:.3f}")
        
        # Salvar modelo
        self.models['failure_predictor'] = best_model
        self.scalers['failure_predictor'] = scaler
        self.encoders['failure_predictor'] = {'test_type': le_test_type, 'business_impact': le_business}
        
        with open('models/failure_predictor.pkl', 'wb') as f:
            pickle.dump(best_model, f)
        with open('models/failure_predictor_scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        
        # Salvar resultados
        results = {
            'model_type': 'RandomForestClassifier',
            'accuracy': accuracy,
            'auc_roc': auc_roc,
            'f1_score': grid_search.best_score_,
            'best_params': grid_search.best_params_,
            'feature_importance': feature_importance,
            'training_date': datetime.now().isoformat()
        }
        
        with open('reports_ml/failure_prediction_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        self.training_results['failure_prediction'] = results
        
        print(f"\n💾 Modelo salvo em: models/failure_predictor.pkl")
        print(f"📊 Resultados salvos em: reports_ml/failure_prediction_results.json")
        
        return best_model, scaler
    
    def workshop_2_test_prioritization(self, df: pd.DataFrame):
        """Workshop 2: Treinar modelo para priorização de testes"""
        print("\n" + "="*60)
        print("🎯 WORKSHOP 2: PRIORIZAÇÃO INTELIGENTE DE TESTES")
        print("="*60)
        
        # Features para priorização
        feature_columns = [
            'execution_time', 'code_coverage', 'complexity_score',
            'failure_count', 'lines_of_code', 'dependency_count'
        ]
        
        # Encoding
        le_test_type = LabelEncoder()
        le_business = LabelEncoder()
        
        df_encoded = df.copy()
        df_encoded['test_type_encoded'] = le_test_type.fit_transform(df['test_type'])
        df_encoded['business_impact_encoded'] = le_business.fit_transform(df['business_impact'])
        
        feature_columns.extend(['test_type_encoded', 'business_impact_encoded'])
        
        X = df_encoded[feature_columns]
        y = df_encoded['test_priority']  # Regressão (0-1)
        
        print(f"📊 Dataset: {len(X)} amostras para regressão")
        print(f"   • Prioridade média: {y.mean():.3f}")
        print(f"   • Desvio padrão: {y.std():.3f}")
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normalização
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        print(f"\n🔧 Treinando modelo Gradient Boosting...")
        
        # Hyperparameter tuning para regressão
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.1, 0.2]
        }
        
        gbr = GradientBoostingRegressor(random_state=42)
        grid_search = GridSearchCV(
            gbr, param_grid, cv=5, scoring='r2', n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X_train_scaled, y_train)
        best_model = grid_search.best_estimator_
        
        # Avaliação
        y_pred = best_model.predict(X_test_scaled)
        r2_score = best_model.score(X_test_scaled, y_test)
        mse = np.mean((y_test - y_pred) ** 2)
        
        print(f"\n📈 RESULTADOS DO MODELO:")
        print(f"   • Melhores parâmetros: {grid_search.best_params_}")
        print(f"   • R² Score: {r2_score:.3f}")
        print(f"   • MSE: {mse:.4f}")
        print(f"   • R² Score (CV): {grid_search.best_score_:.3f}")
        
        # Feature importance
        feature_importance = dict(zip(feature_columns, best_model.feature_importances_))
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n🔍 Top 5 Features Mais Importantes:")
        for feature, importance in sorted_features[:5]:
            print(f"   • {feature}: {importance:.3f}")
        
        # Salvar modelo
        self.models['test_prioritizer'] = best_model
        self.scalers['test_prioritizer'] = scaler
        
        with open('models/test_prioritizer.pkl', 'wb') as f:
            pickle.dump(best_model, f)
        with open('models/test_prioritizer_scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        
        # Salvar resultados
        results = {
            'model_type': 'GradientBoostingRegressor',
            'r2_score': r2_score,
            'mse': mse,
            'cv_r2_score': grid_search.best_score_,
            'best_params': grid_search.best_params_,
            'feature_importance': feature_importance,
            'training_date': datetime.now().isoformat()
        }
        
        with open('reports_ml/test_prioritization_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        self.training_results['test_prioritization'] = results
        
        print(f"\n💾 Modelo salvo em: models/test_prioritizer.pkl")
        print(f"📊 Resultados salvos em: reports_ml/test_prioritization_results.json")
        
        return best_model, scaler
    
    def workshop_3_flakiness_detection(self, df: pd.DataFrame):
        """Workshop 3: Detectar testes flaky"""
        print("\n" + "="*60)
        print("🎯 WORKSHOP 3: DETECÇÃO DE TESTES FLAKY")
        print("="*60)
        
        # Features específicas para flakiness
        feature_columns = [
            'failure_count', 'complexity_score', 'network_calls',
            'io_operations', 'execution_time', 'dependency_count'
        ]
        
        X = df[feature_columns]
        y = df['is_flaky']
        
        print(f"📊 Dataset: {len(X)} amostras")
        print(f"   • Testes flaky: {y.sum()} ({y.mean():.1%})")
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normalização
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        print(f"\n🔧 Treinando modelo Random Forest para flakiness...")
        
        # Modelo otimizado para classe desbalanceada
        rf = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            class_weight='balanced',  # Importante para classes desbalanceadas
            random_state=42
        )
        
        rf.fit(X_train_scaled, y_train)
        
        # Avaliação
        y_pred = rf.predict(X_test_scaled)
        y_proba = rf.predict_proba(X_test_scaled)[:, 1]
        
        accuracy = rf.score(X_test_scaled, y_test)
        auc_roc = roc_auc_score(y_test, y_proba)
        
        print(f"\n📈 RESULTADOS DO MODELO:")
        print(f"   • Acurácia: {accuracy:.3f}")
        print(f"   • AUC-ROC: {auc_roc:.3f}")
        
        print(f"\n📋 Relatório de Classificação:")
        print(classification_report(y_test, y_pred))
        
        # Feature importance
        feature_importance = dict(zip(feature_columns, rf.feature_importances_))
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n🔍 Features Mais Importantes para Flakiness:")
        for feature, importance in sorted_features:
            print(f"   • {feature}: {importance:.3f}")
        
        # Salvar modelo
        self.models['flakiness_detector'] = rf
        self.scalers['flakiness_detector'] = scaler
        
        with open('models/flakiness_detector.pkl', 'wb') as f:
            pickle.dump(rf, f)
        with open('models/flakiness_detector_scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        
        # Salvar resultados
        results = {
            'model_type': 'RandomForestClassifier',
            'accuracy': accuracy,
            'auc_roc': auc_roc,
            'feature_importance': feature_importance,
            'training_date': datetime.now().isoformat()
        }
        
        with open('reports_ml/flakiness_detection_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        self.training_results['flakiness_detection'] = results
        
        print(f"\n💾 Modelo salvo em: models/flakiness_detector.pkl")
        
        return rf, scaler
    
    def demonstrate_predictions(self, df: pd.DataFrame):
        """Demonstra como usar os modelos treinados"""
        print("\n" + "="*60)
        print("🔮 DEMONSTRAÇÃO: USANDO OS MODELOS TREINADOS")
        print("="*60)
        
        # Selecionar alguns testes para demonstração
        sample_tests = df.sample(5, random_state=42)
        
        print(f"\n🧪 Analisando 5 testes de exemplo:")
        
        for idx, test in sample_tests.iterrows():
            print(f"\n--- Teste: {test['test_name']} ---")
            print(f"Tipo: {test['test_type']} | Impacto: {test['business_impact']}")
            print(f"Tempo execução: {test['execution_time']:.1f}s | Cobertura: {test['code_coverage']:.1f}%")
            
            # Predição de falha
            if 'failure_predictor' in self.models:
                # Preparar features (simplificado)
                features = [
                    test['execution_time'], test['code_coverage'], test['complexity_score'],
                    test['failure_count'], test['days_since_last_failure'], test['recent_changes'],
                    test['dependency_count'], test['io_operations'], test['network_calls'],
                    0, 0  # Placeholders para encoding categórico
                ]
                
                features_scaled = self.scalers['failure_predictor'].transform([features])\n                failure_prob = self.models['failure_predictor'].predict_proba(features_scaled)[0][1]
                print(f"🎯 Probabilidade de falha: {failure_prob:.1%}")
            
            # Predição de prioridade
            if 'test_prioritizer' in self.models:
                priority_features = [
                    test['execution_time'], test['code_coverage'], test['complexity_score'],
                    test['failure_count'], test['lines_of_code'], test['dependency_count'],
                    0, 0  # Placeholders
                ]
                
                priority_scaled = self.scalers['test_prioritizer'].transform([priority_features])
                priority_score = self.models['test_prioritizer'].predict(priority_scaled)[0]
                print(f"⭐ Score de prioridade: {priority_score:.3f}")
            
            # Detecção de flakiness
            if 'flakiness_detector' in self.models:
                flaky_features = [
                    test['failure_count'], test['complexity_score'], test['network_calls'],
                    test['io_operations'], test['execution_time'], test['dependency_count']
                ]
                
                flaky_scaled = self.scalers['flakiness_detector'].transform([flaky_features])
                flaky_prob = self.models['flakiness_detector'].predict_proba(flaky_scaled)[0][1]
                print(f"🔄 Probabilidade de ser flaky: {flaky_prob:.1%}")
            
            # Valores reais (ground truth)
            print(f"✅ Real: Falha={test['will_fail']}, Prioridade={test['test_priority']:.3f}, Flaky={test['is_flaky']}")
    
    def generate_summary_report(self):
        """Gera relatório final do workshop"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO FINAL DO WORKSHOP")
        print("="*60)
        
        summary = {
            'workshop_date': datetime.now().isoformat(),
            'models_trained': len(self.training_results),
            'results': self.training_results
        }
        
        print(f"\n🎯 Modelos Treinados: {len(self.training_results)}")
        
        for model_name, results in self.training_results.items():
            print(f"\n--- {model_name.upper().replace('_', ' ')} ---")
            print(f"Tipo: {results['model_type']}")
            
            if 'accuracy' in results:
                print(f"Acurácia: {results['accuracy']:.3f}")
            if 'auc_roc' in results:
                print(f"AUC-ROC: {results['auc_roc']:.3f}")
            if 'r2_score' in results:
                print(f"R² Score: {results['r2_score']:.3f}")
        
        # Salvar relatório completo
        with open('reports_ml/workshop_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Relatório completo salvo em: reports_ml/workshop_summary.json")
        
        # Próximos passos
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print(f"1. Experimente com seus próprios dados de teste")
        print(f"2. Ajuste os hiperparâmetros dos modelos")
        print(f"3. Implemente os modelos no seu pipeline de CI/CD")
        print(f"4. Monitore a performance dos modelos em produção")
        print(f"5. Colete feedback e retreine os modelos regularmente")

def main():
    """Executa o workshop completo de ML para QA"""
    print("🎓 ML TRAINING WORKSHOP PARA QA ENGINEERS")
    print("=" * 60)
    print("Aprenda a treinar modelos de Machine Learning para Testing!")
    print()
    
    workshop = MLTrainingWorkshop()
    
    # Gerar dados sintéticos
    df = workshop.generate_synthetic_test_data(n_samples=1000)
    
    # Workshop 1: Predição de falhas
    workshop.workshop_1_failure_prediction(df)
    
    # Workshop 2: Priorização de testes
    workshop.workshop_2_test_prioritization(df)
    
    # Workshop 3: Detecção de flakiness
    workshop.workshop_3_flakiness_detection(df)
    
    # Demonstração prática
    workshop.demonstrate_predictions(df)
    
    # Relatório final
    workshop.generate_summary_report()
    
    print(f"\n🎉 Workshop concluído com sucesso!")
    print(f"Você agora tem 3 modelos ML treinados para QA!")

if __name__ == "__main__":
    main()