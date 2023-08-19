import dotenv from "dotenv";
import cors from "cors";
import express, { Request, Response } from "express";
import generate from "./generate";

dotenv.config();

const app = express();
const port = process.env.PORT ?? 8000;
app.use(cors());
app.use(express.json());
app.use(express.text());
app.use(express.urlencoded({ extended: true }));

app.post("/generate", async (req: Request, res: Response) => {
  try {
    const { message } = req.body;
    if (!message) {
      res
        .status(500)
        .send({
          error:
            'Message is required. Example JSON payload: {"message": "my request"}',
        });
      return;
    }

    const answer = await generate(message);

    // "$RESPONSE.answer.0.value"
    // res.send(answer);
    res.send({ answer: [{value: answer}] });

  } catch (error) {
    // console.log(error);
    res.status(500).send({ error });
  }
});

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});
