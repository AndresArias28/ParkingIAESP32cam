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
  int? carrosDisponibles;

  @override
  void initState() {
    super.initState();

    database = FirebaseDatabase.instanceFor(
      app: Firebase.app(),
      databaseURL: 'https://parkingia-default-rtdb.firebaseio.com',
    );

    databaseRef = database.ref();

    obtenerDatos();
  }

  Future<void> obtenerDatos() async {
    final snapshot = await databaseRef.child('estado/dispCarro').get();
    if (snapshot.exists) {
       final valor = snapshot.value;

      print('Valor recibido desde Firebase: $valor');
      setState(() {
        carrosDisponibles = snapshot.value as int?;
      });
      print(snapshot.value);
    } else {
      print('No se encontraron datos.');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text('Carros disponibles:'),
            Text(
              carrosDisponibles != null ? '$carrosDisponibles' : 'Cargando...',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
    );
  }
}
