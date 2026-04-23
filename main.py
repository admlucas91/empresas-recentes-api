import React, { useState } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Alert,
  ScrollView,
} from 'react-native';

const API_BASE = 'https://empresas-recentes-api.onrender.com';

function diasDesde(dataIso) {
  const hoje = new Date();
  const data = new Date(dataIso);
  const diff = hoje.getTime() - data.getTime();
  return Math.floor(diff / (1000 * 60 * 60 * 24));
}

function labelEnergia(score) {
  if (score >= 90) return 'Consumo muito alto';
  if (score >= 80) return 'Consumo alto';
  return 'Consumo moderado';
}

function corEnergia(score) {
  if (score >= 90) return '#ef4444';
  if (score >= 80) return '#f59e0b';
  return '#22c55e';
}

export default function App() {
  const [cidade, setCidade] = useState('');
  const [bairro, setBairro] = useState('');
  const [resultados, setResultados] = useState([]);
  const [leads, setLeads] = useState([]);
  const [status, setStatus] = useState('');

  async function pesquisar() {
    try {
      setStatus('Pesquisando empresas...');
      const url =
        `${API_BASE}/empresas/recentes` +
        `?cidade=${encodeURIComponent(cidade)}` +
        `&bairro=${encodeURIComponent(bairro)}` +
        `&dias=90` +
        `&energia_minima=80`;

      const resposta = await fetch(url);
      if (!resposta.ok) throw new Error(`Erro HTTP ${resposta.status}`);

      const dados = await resposta.json();
      setResultados(dados);
      setStatus(`Encontradas: ${dados.length}`);
    } catch (erro) {
      setResultados([]);
      setStatus('Erro ao pesquisar empresas');
      console.error(erro);
    }
  }

  async function carregarLeads() {
    try {
      const resposta = await fetch(`${API_BASE}/leads`);
      const dados = await resposta.json();
      setLeads(dados);
    } catch (erro) {
      console.error(erro);
    }
  }

  async function salvarLead(empresa) {
    try {
      const resposta = await fetch(`${API_BASE}/leads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          empresa_id: empresa.id,
          status: 'Novo',
          prioridade: 'Alta',
          observacao: '',
        }),
      });

      const dados = await resposta.json();

      if (dados.erro) {
        Alert.alert('Aviso', dados.erro);
        return;
      }

      Alert.alert('Sucesso', `Lead salvo: ${dados.empresa_nome}`);
      carregarLeads();
    } catch (erro) {
      Alert.alert('Erro', 'Não foi possível salvar o lead');
      console.error(erro);
    }
  }

  function limpar() {
    setCidade('');
    setBairro('');
    setResultados([]);
    setStatus('');
  }

  React.useEffect(() => {
    carregarLeads();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.titulo}>Empresas Recentes</Text>
        <Text style={styles.subtitulo}>
          Busque por cidade ou bairro e salve os melhores leads comerciais.
        </Text>

        <TextInput
          style={styles.input}
          placeholder="Cidade. Ex.: Senador Canedo"
          placeholderTextColor="#94a3b8"
          value={cidade}
          onChangeText={setCidade}
        />

        <TextInput
          style={styles.input}
          placeholder="Bairro. Ex.: Centro"
          placeholderTextColor="#94a3b8"
          value={bairro}
          onChangeText={setBairro}
        />

        <TouchableOpacity style={styles.botaoBuscar} onPress={pesquisar}>
          <Text style={styles.textoBotao}>Pesquisar empresas</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.botaoLeads} onPress={carregarLeads}>
          <Text style={styles.textoBotaoEscuro}>Atualizar leads</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.botaoLimpar} onPress={limpar}>
          <Text style={styles.textoBotaoEscuro}>Limpar busca</Text>
        </TouchableOpacity>

        <Text style={styles.status}>{status}</Text>

        <Text style={styles.secaoTitulo}>Resultados</Text>
        <FlatList
          data={resultados}
          keyExtractor={(item) => `empresa-${item.id}`}
          scrollEnabled={false}
          ListEmptyComponent={
            status && resultados.length === 0 ? (
              <Text style={styles.vazio}>
                Nenhuma empresa recente com consumo alto encontrada.
              </Text>
            ) : null
          }
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View style={styles.topoCard}>
                <Text style={styles.nome}>{item.nome}</Text>
                <View
                  style={[
                    styles.badge,
                    { backgroundColor: corEnergia(item.energy_score) },
                  ]}
                >
                  <Text style={styles.badgeTexto}>{item.energy_score}</Text>
                </View>
              </View>

              <Text style={styles.linha}>Cidade: {item.cidade}</Text>
              <Text style={styles.linha}>Bairro: {item.bairro}</Text>
              <Text style={styles.linha}>Categoria: {item.categoria}</Text>
              <Text style={styles.linha}>Endereço: {item.endereco}</Text>
              <Text style={styles.linha}>
                Abertura: {item.aberto_em} ({diasDesde(item.aberto_em)} dias)
              </Text>
              <Text style={styles.energia}>
                {labelEnergia(item.energy_score)}
              </Text>

              <TouchableOpacity
                style={styles.botaoSalvarLead}
                onPress={() => salvarLead(item)}
              >
                <Text style={styles.textoBotao}>Salvar lead</Text>
              </TouchableOpacity>
            </View>
          )}
        />

        <Text style={styles.secaoTitulo}>Leads salvos</Text>
        <FlatList
          data={leads}
          keyExtractor={(item) => `lead-${item.id}`}
          scrollEnabled={false}
          ListEmptyComponent={
            <Text style={styles.vazio}>Nenhum lead salvo ainda.</Text>
          }
          renderItem={({ item }) => (
            <View style={styles.cardLead}>
              <Text style={styles.nome}>{item.empresa_nome}</Text>
              <Text style={styles.linha}>Status: {item.status}</Text>
              <Text style={styles.linha}>Prioridade: {item.prioridade}</Text>
              <Text style={styles.linha}>Cidade: {item.cidade}</Text>
              <Text style={styles.linha}>Categoria: {item.categoria}</Text>
              <Text style={styles.linha}>Endereço: {item.endereco}</Text>
            </View>
          )}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#081226',
    paddingHorizontal: 16,
    paddingTop: 18,
  },
  titulo: {
    color: '#38bdf8',
    fontSize: 30,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitulo: {
    color: '#cbd5e1',
    textAlign: 'center',
    marginBottom: 18,
    lineHeight: 20,
  },
  input: {
    backgroundColor: '#16233b',
    color: '#fff',
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 14,
    marginBottom: 12,
    fontSize: 16,
  },
  botaoBuscar: {
    backgroundColor: '#38bdf8',
    paddingVertical: 15,
    borderRadius: 14,
    marginBottom: 10,
  },
  botaoLeads: {
    backgroundColor: '#facc15',
    paddingVertical: 15,
    borderRadius: 14,
    marginBottom: 10,
  },
  botaoLimpar: {
    backgroundColor: '#e2e8f0',
    paddingVertical: 15,
    borderRadius: 14,
    marginBottom: 14,
  },
  botaoSalvarLead: {
    backgroundColor: '#22c55e',
    paddingVertical: 12,
    borderRadius: 12,
    marginTop: 10,
  },
  textoBotao: {
    textAlign: 'center',
    color: '#0f172a',
    fontWeight: 'bold',
    fontSize: 16,
  },
  textoBotaoEscuro: {
    textAlign: 'center',
    color: '#111827',
    fontWeight: 'bold',
    fontSize: 16,
  },
  status: {
    color: '#fff',
    textAlign: 'center',
    marginBottom: 12,
    fontWeight: 'bold',
    fontSize: 16,
  },
  secaoTitulo: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 10,
    marginBottom: 10,
  },
  card: {
    backgroundColor: '#16233b',
    padding: 14,
    borderRadius: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#24324d',
  },
  cardLead: {
    backgroundColor: '#1b2942',
    padding: 14,
    borderRadius: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#31415f',
  },
  topoCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 10,
    marginBottom: 6,
  },
  nome: {
    color: '#fff',
    fontSize: 17,
    fontWeight: 'bold',
    flex: 1,
  },
  linha: {
    color: '#dbe4f0',
    marginBottom: 3,
  },
  energia: {
    color: '#fbbf24',
    marginTop: 6,
    fontWeight: 'bold',
  },
  badge: {
    minWidth: 46,
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 999,
    alignItems: 'center',
  },
  badgeTexto: {
    color: '#fff',
    fontWeight: 'bold',
  },
  vazio: {
    color: '#cbd5e1',
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 16,
  },
});
