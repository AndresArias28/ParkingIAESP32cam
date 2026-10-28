import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';

class ParkingStation extends StatefulWidget {
  const ParkingStation({super.key});

  @override
  State<ParkingStation> createState() => _ParkingStationState();
}

class _ParkingStationState extends State<ParkingStation> {
  late final FirebaseDatabase database;
  late final DatabaseReference databaseRef;
  late final DatabaseReference estadoRef;
  int? carrosDisponibles;

  @override
  void initState() {
    super.initState();

    database = FirebaseDatabase.instanceFor(
      app: Firebase.app(),
      databaseURL: 'https://parkingia-default-rtdb.firebaseio.com',
    );

    //databaseRef = database.ref();
    estadoRef = database.ref('estado');
    //obtenerDatos();
  }

  // Future<void> obtenerDatos() async {
  //   final snapshot = await databaseRef.child('estado/dispCarro').get();
  //   if (snapshot.exists) {
  //     final valor = snapshot.value;

  //     print('Valor recibido desde Firebase: $valor');
  //     setState(() {
  //       carrosDisponibles = snapshot.value as int?;
  //     });
  //     print(snapshot.value);
  //   } else {
  //     print('No se encontraron datos.');
  //   }
  // }

  @override
  Widget build(BuildContext context) {
    // final DatabaseReference estadoRef = FirebaseDatabase.instance.ref(
    //   'estado/dispCarro',
    // );

    return Scaffold(
      appBar: AppBar(title: const Text('Parking Station')),

      body: StreamBuilder<DatabaseEvent>(
        stream: estadoRef.onValue,

        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return const Center(child: Text('Error cargando información'));
          }

          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }

          final value = snapshot.data!.snapshot.value;

          if (value == null) {
            return const Center(child: Text('No hay información'));
          }

          final data = Map<String, dynamic>.from(value as Map);

          final int dispCarro = data['dispCarro'] ?? 0;

          final int dispMoto = data['dispMoto'] ?? 0;

          final int ocupadosCarro = data['ocupadosCarro'] ?? 0;

          final int ocupadosMoto = data['ocupadosMoto'] ?? 0;

          return Padding(
            padding: const EdgeInsets.all(20),

            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,

              children: [
                Text(
                  'Carros disponibles: $dispCarro',
                  style: const TextStyle(fontSize: 24),
                ),

                Text(
                  'Carros ocupados: $ocupadosCarro',
                  style: const TextStyle(fontSize: 20),
                ),

                const SizedBox(height: 30),

                Text(
                  'Motos disponibles: $dispMoto',
                  style: const TextStyle(fontSize: 24),
                ),

                Text(
                  'Motos ocupadas: $ocupadosMoto',
                  style: const TextStyle(fontSize: 20),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
