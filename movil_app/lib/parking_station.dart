import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:flutter/material.dart';

class ParkingStation extends StatefulWidget {
  const ParkingStation({super.key});

  @override
  State<ParkingStation> createState() => _ParkingStationState();
}

class _ParkingStationState extends State<ParkingStation> {
  late final DatabaseReference parkingRef;

  @override
  void initState() {
    super.initState();
    final database = FirebaseDatabase.instanceFor(
      app: Firebase.app(),
      databaseURL: 'https://parkingia-default-rtdb.firebaseio.com',
    );
    parkingRef = database.ref('parking');
  }

  Map<String, dynamic> asMap(Object? value) =>
      value is Map ? Map<String, dynamic>.from(value) : {};

  int asInt(Object? value) => value is num ? value.toInt() : 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Parking IA')),
      body: StreamBuilder<DatabaseEvent>(
        stream: parkingRef.onValue,
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return const Center(child: Text('No se pudo leer Firebase'));
          }
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final value = snapshot.data!.snapshot.value;
          if (value == null) {
            return const Center(child: Text('Esperando el primer evento del parqueadero'));
          }
          final parking = asMap(value);
          final state = asMap(parking['state']);
          final occupied = asMap(state['occupied']);
          final available = asMap(state['available']);
          final config = asMap(parking['config']);
          final capacity = asMap(config['capacity']);
          final events = asMap(parking['events']).entries.toList()
            ..sort((a, b) => asInt(asMap(b.value)['timestamp'])
                .compareTo(asInt(asMap(a.value)['timestamp'])));

          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              const Text('Cupos en tiempo real',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Card(child: ListTile(
                title: const Text('Carros'),
                subtitle: Text('Ocupados: ${asInt(occupied['car'])} de ${asInt(capacity['car'])}'),
                trailing: Text('${asInt(available['car'])} libres',
                    style: const TextStyle(fontSize: 18)),
              )),
              Card(child: ListTile(
                title: const Text('Motos'),
                subtitle: Text('Ocupadas: ${asInt(occupied['motorcycle'])} de ${asInt(capacity['motorcycle'])}'),
                trailing: Text('${asInt(available['motorcycle'])} libres',
                    style: const TextStyle(fontSize: 18)),
              )),
              const SizedBox(height: 24),
              const Text('Eventos recientes',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              if (events.isEmpty) const ListTile(title: Text('Aún no hay movimientos')),
              for (final entry in events.take(5))
                Builder(builder: (context) {
                  final event = asMap(entry.value);
                  final vehicle = event['type'] == 'car' ? 'Carro' : 'Moto';
                  final action = event['action'] == 'in' ? 'entró' : 'salió';
                  final timestamp = asInt(event['timestamp']);
                  final when = timestamp > 0
                      ? DateTime.fromMillisecondsSinceEpoch(timestamp).toLocal()
                      : null;
                  return ListTile(
                    leading: Icon(event['action'] == 'in'
                        ? Icons.login : Icons.logout),
                    title: Text('$vehicle $action'),
                    subtitle: Text('${event['camera'] ?? ''}${when == null ? '' : ' · $when'}'),
                  );
                }),
            ],
          );
        },
      ),
    );
  }
}
