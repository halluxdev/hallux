import dotenv from 'dotenv';
import cors from 'cors';
import express, { Request, Response } from 'express';
import generate from './generate';

let testVar;

var global = window;

dotenv.config();

const app = express();
const port = process.env.PORT ?? 8000;
app.use(cors());
app.use(express.json());
app.use(express.text());
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));

// app.get('/', (req: Request, res: Response)

app.post('/generate', async (req: Request, res: Response) => {
  try {
    const {message} = req.body;
    if(!message) {
      res.status(500).send({error: 'Message is required. Example JSON payload: {"message": "my request"}'});
      return;
    }

    const answer = await generate(message);

    res.send({answer});
  } catch (error) {
    console.log(error);

    res.status(500).send({error});
  }
});

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});